"""
╔══════════════════════════════════════════════════════════════╗
║         FIBLAB ROBOT — Webhook Trading Server                ║
║         Charlie Joe 1972 — Juin 2026                         ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from collections import deque

app = Flask(__name__)

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
TELEGRAM_TOKEN     = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_CHAT_ID_2 = os.environ.get("TELEGRAM_CHAT_ID_2", "")

# ─────────────────────────────────────────────
# PROFILS UTILISATEURS — indépendants par chat_id
# ─────────────────────────────────────────────
def default_profile():
    return {
        "paused": False,
        "mode": "swing",
        "tf_custom": {"72":False,"90":False,"96":False,"144":False,"160":False,"288":False}
    }

user_profiles = {}

def get_profile(chat_id: str) -> dict:
    if not chat_id: return default_profile()
    if chat_id not in user_profiles:
        user_profiles[chat_id] = default_profile()
    return user_profiles[chat_id]

# État admin global (pause totale)
robot_state = {"paused": False}

# ─────────────────────────────────────────────
# ASSETS
# ─────────────────────────────────────────────
ASSET_GROUPS = {
    "xau":    {"XAUUSD","XAU/USD","GOLD","GC1!","MGC1!"},
    "dax":    {"DE30EUR","GER30","DAX40","FDAX1!","DE30","GER40","DAX"},
    "solana": {"SOLUSDT","SOL/USD","SOLUSDT.P","SOLUSD"},
    "btc":    {"BTCUSDT","BTC/USD","BTCUSDT.P","BTCUSD","BTCUSDTP"},
    "stocks": {"TSLA","HOOD","CELH","TTD","PLTR","AMZN","NVDA","AAPL","META","GOOGL","MSFT","SOFI"},
}

ASSET_META = {
    "xau":    {"label":"XAU/USD",  "emoji":"🥇","tv":"https://www.tradingview.com/chart/?symbol=OANDA:XAUUSD"},
    "dax":    {"label":"DAX",      "emoji":"🇩🇪","tv":"https://www.tradingview.com/chart/?symbol=OANDA:DE30EUR"},
    "solana": {"label":"SOLANA",   "emoji":"💎","tv":"https://www.tradingview.com/chart/?symbol=BITGET:SOLUSDT.P"},
    "btc":    {"label":"BITCOIN",  "emoji":"₿", "tv":"https://www.tradingview.com/chart/?symbol=BITGET:BTCUSDT.P"},
    "stocks": {"label":"STOCKS",   "emoji":"📈","tv":"https://www.tradingview.com/chart/?symbol=NASDAQ:"},
}

def get_asset_group(asset: str) -> str:
    if not asset: return None
    a = asset.upper().replace("-","").replace(".","").replace("/","")
    for group, assets in ASSET_GROUPS.items():
        for ref in assets:
            if a == ref.upper().replace("-","").replace(".","").replace("/",""):
                return group
    return None

def get_tv_link(asset: str, group: str) -> str:
    if not group: return ""
    meta = ASSET_META.get(group, {})
    if group == "stocks" and asset:
        return f"https://www.tradingview.com/chart/?symbol=NASDAQ:{asset}"
    return meta.get("tv","")

# Historiques
alert_history = deque(maxlen=200)
histories = {g: deque(maxlen=100) for g in ASSET_GROUPS}

# ─────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────
def normalize_timeframe(tf: str) -> str:
    numeric_map = {
        "1":"M1","2":"M2","3":"M3","4":"M4","5":"M5","10":"M10",
        "15":"M15","30":"M30","45":"M45",
        "60":"H1","120":"H2","180":"H3","240":"H4",
        "360":"H6","480":"H8","720":"H12",
        "1440":"D1","10080":"W1","43200":"MN",
        "72":"72m","90":"90m","96":"96m",
        "144":"144m","160":"160m","288":"288m",
    }
    return numeric_map.get(tf, tf)

def parse_fiblab_message(raw: str) -> dict:
    result = {
        "raw": raw.strip(), "type":None, "asset":None,
        "timeframe":None, "side":None, "price":None,
        "scope":None, "timestamp": datetime.utcnow().isoformat(),
    }
    if "ATR PROXIMITY" in raw.upper():
        result["type"] = "ATR Proximity"
        m = re.search(r'TF:\s*([^\n\r|]+)', raw, re.IGNORECASE)
        if m: result["timeframe"] = normalize_timeframe(m.group(1).strip().upper())
        m = re.search(r'Side:\s*(Support|Resistance)', raw, re.IGNORECASE)
        if m: result["side"] = m.group(1).capitalize()
        m = re.search(r'Origin entry nearby:\s*([\d.]+)', raw, re.IGNORECASE)
        if m: result["price"] = float(m.group(1))
        result["scope"] = "Pure"
        return result

    if "—" in raw:
        parts = raw.split("—", 1)
        result["type"] = parts[0].strip()
        rest = parts[1].strip()
    else:
        rest = raw

    asset_tf = re.search(
        r'([A-Z0-9./]+)\s+([0-9]+[SMHD]?|[HMD][0-9]+|Daily|Weekly|Monthly)',
        rest, re.IGNORECASE
    )
    if asset_tf:
        result["asset"] = asset_tf.group(1).upper()
        result["timeframe"] = normalize_timeframe(asset_tf.group(2).upper())

    m = re.search(r'Side:\s*(Support|Resistance)', rest, re.IGNORECASE)
    if m: result["side"] = m.group(1).capitalize()
    m = re.search(r'Price:\s*([\d.]+)', rest)
    if m: result["price"] = float(m.group(1))
    m = re.search(r'Scope:\s*(Pure|Non-Pure)', rest, re.IGNORECASE)
    if m: result["scope"] = m.group(1)
    return result

# ─────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────
TF_WEIGHT = {
    "M1":0,"M2":0,"M3":0,"M4":0,"M5":1,"M10":1,"M15":1,"M30":1,"M45":1,
    "H1":2,"H2":2,"H3":2,
    "H4":3,"H6":3,"H8":3,"H12":3,
    "D1":4,"1D":4,"D":4,"DAILY":4,
    "W1":4,"1W":4,"W":4,"WEEKLY":4,"MN":4,"MONTHLY":4,
    "72m":1,"90m":1,"96m":1,"144m":2,"160m":2,"288m":2,
}

TYPE_SCORES = {
    "origin untouched":5,"origin first touch":4,
    "broken origin first touch":4,"broken first touch":3,
    "break first touch":3,"atr proximity":3,
    "break created":2,"origin broken":2,"bsut created":2,
    "origin touched":1,
}

def compute_score(parsed: dict) -> dict:
    score, details = 0, []
    alert_type = (parsed.get("type") or "").lower()
    tf    = (parsed.get("timeframe") or "").upper()
    scope = (parsed.get("scope") or "").lower()

    for key, val in TYPE_SCORES.items():
        if key in alert_type:
            score += val
            details.append(f"Type '{parsed['type']}' → +{val}")
            break

    if scope == "pure":
        score += 2
        details.append("Scope Pure → +2")

    tf_score = TF_WEIGHT.get(tf, TF_WEIGHT.get(tf.lower(), 0))
    if tf_score > 0:
        score += tf_score
        details.append(f"Timeframe {tf} → +{tf_score}")

    if "first touch" in alert_type:
        score += 2
        details.append("Première visite (First Touch) → +2")

    if score >= 8:   level, emoji = "PRIORITAIRE","🔴"
    elif score >= 5: level, emoji = "SECONDAIRE", "⚠️"
    else:            level, emoji = "INFO",        "📊"

    return {"score":score,"level":level,"emoji":emoji,"details":details}

# ─────────────────────────────────────────────
# FILTRES — basés sur le profil utilisateur
# ─────────────────────────────────────────────
TF_SWING  = {"H4","H6","H8","H12","D1","D2","D3","D4","D5","D6","D7",
             "W1","MN","1D","2D","3D","4D","5D","6D","7D","1W","4H","8H","12H"}
TF_SCALP  = {"M1","M2","M3","M4","M5","M10","M15","M30","M45","H1","H2","H3","H4","4H"}
TF_CUSTOM = {"72m","90m","96m","144m","160m","288m"}
TF_DAILY  = {"D1","D2","D3","D4","D5","D6","D7","1D","2D","3D","4D","5D","6D","7D","W1","MN","1W"}

TYPES_ALWAYS     = {"origin first touch","origin untouched","atr proximity",
                    "break first touch","broken first touch","broken origin first touch"}
TYPES_DAILY_ONLY = {"origin touched"}
TYPES_SCORE_MIN  = {"bsut created": 6}
TYPES_IGNORED    = {"break created"}

def should_notify(parsed: dict, scoring: dict, profile: dict) -> tuple:
    alert_type = (parsed.get("type") or "").lower()
    tf         = (parsed.get("timeframe") or "").upper()
    tf_lower   = tf.lower()
    mode       = profile["mode"]

    if tf_lower in TF_CUSTOM:
        key = tf_lower.replace("m","")
        if not profile["tf_custom"].get(key, False):
            return False, f"TF custom '{tf}' désactivé"
    elif mode == "swing" and tf not in TF_SWING:
        return False, f"Mode SWING : TF '{tf}' ignoré"
    elif mode == "scalp" and tf not in TF_SCALP:
        return False, f"Mode SCALP : TF '{tf}' ignoré"
    elif mode == "both" and tf not in TF_SWING | TF_SCALP:
        return False, f"TF '{tf}' non reconnu"

    for ignored in TYPES_IGNORED:
        if ignored in alert_type:
            return False, f"Type ignoré"

    for t, min_score in TYPES_SCORE_MIN.items():
        if t in alert_type:
            if scoring["score"] < min_score:
                return False, f"BSUT score {scoring['score']} < {min_score}"
            return True, "ok"

    for t in TYPES_DAILY_ONLY:
        if t in alert_type:
            if tf not in TF_DAILY:
                return False, f"Origin Touched nécessite Daily+"
            return True, "ok"

    for t in TYPES_ALWAYS:
        if t in alert_type:
            return True, "ok"

    if scoring["score"] >= 5:
        return True, "ok"

    return False, f"Score insuffisant"

# ─────────────────────────────────────────────
# TELEGRAM
# ─────────────────────────────────────────────
def send_telegram(message: str, chat_id: str = None):
    if not TELEGRAM_TOKEN: return False
    target = chat_id or TELEGRAM_CHAT_ID
    if not target: return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": target, "text": message, "parse_mode": "HTML"},
            timeout=10
        )
        return r.status_code == 200
    except Exception as e:
        print(f"[TELEGRAM] Erreur : {e}")
        return False

def format_telegram_message(parsed: dict, scoring: dict, profile: dict = None) -> str:
    asset   = parsed.get("asset") or None
    group   = get_asset_group(asset) if asset else None
    meta    = ASSET_META.get(group, {"emoji":"📡","label":asset or "?"})
    is_atr  = "atr" in (parsed.get("type") or "").lower()
    tv_link = get_tv_link(asset, group)
    mode    = (profile or {}).get("mode","swing")

    side_emoji    = "🟢" if parsed.get("side") == "Support" else "🔴"
    scope_tag     = "✅ Pure" if parsed.get("scope") == "Pure" else "⬜ Non-Pure"
    asset_display = f"{meta['emoji']} {asset}" if asset else f"{meta['emoji']} voir chart"
    action = (
        "→ Surveille M1 maintenant\n→ Setup <b>LONG</b> potentiel\n→ SL visé : 5-10 pts"
        if parsed.get("side") == "Support" else
        "→ Surveille M1 maintenant\n→ Setup <b>SHORT</b> potentiel\n→ SL visé : 5-10 pts"
    )

    msg = (
        f"{scoring['emoji']} <b>ALERTE {scoring['level']} — Score {scoring['score']}/15</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Asset    : <b>{asset_display}</b>\n"
        f"Niveau   : <b>{parsed.get('price','?')}</b>\n"
        f"Type     : {'📡 ' if is_atr else ''}{parsed.get('type','?')}\n"
        f"TF       : {parsed.get('timeframe','?')}\n"
        f"Side     : {side_emoji} {parsed.get('side','?')}\n"
        f"Scope    : {scope_tag}\n"
        f"Mode     : {mode.upper()}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Scoring :\n"
    )
    for d in scoring["details"]:
        msg += f"  • {d}\n"

    tv_line = f"\n📈 <a href='{tv_link}'>Ouvrir le chart</a>" if tv_link else ""
    msg += (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Action :\n{action}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {parsed.get('timestamp','')[:19].replace('T',' ')} UTC"
        f"{tv_line}"
    )
    return msg

# ─────────────────────────────────────────────
# COMMANDES TELEGRAM
# ─────────────────────────────────────────────
def handle_telegram_command(text: str, chat_id: str):
    parts   = text.strip().lower().split()
    cmd     = parts[0]
    arg     = parts[1] if len(parts) > 1 else ""
    profile = get_profile(chat_id)

    if cmd == "/mode":
        if arg in ("swing","scalp","both"):
            profile["mode"] = arg
            labels = {"swing":"🔵 SWING (H4+)","scalp":"⚡ SCALP (M1→H4)","both":"🌐 BOTH (tout)"}
            msg = f"✅ Ton mode → <b>{labels[arg]}</b>\n(ne change rien pour les autres utilisateurs)"
        else:
            msg = "Usage : /mode swing | /mode scalp | /mode both"

    elif cmd == "/tf_on":
        if arg in profile["tf_custom"]:
            profile["tf_custom"][arg] = True
            msg = f"✅ TF <b>{arg}m</b> activé pour toi"
        else:
            msg = f"TF '{arg}' inconnu. Disponibles : 72 90 96 144 160 288"

    elif cmd == "/tf_off":
        if arg in profile["tf_custom"]:
            profile["tf_custom"][arg] = False
            msg = f"⛔ TF <b>{arg}m</b> désactivé pour toi"
        else:
            msg = f"TF '{arg}' inconnu. Disponibles : 72 90 96 144 160 288"

    elif cmd == "/tf_status":
        actifs   = [k for k,v in profile["tf_custom"].items() if v]
        inactifs = [k for k,v in profile["tf_custom"].items() if not v]
        msg = (
            f"📊 <b>Ton profil TF</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Mode    : <b>{profile['mode'].upper()}</b>\n"
            f"✅ TF+  : {', '.join(actifs) if actifs else 'aucun'}\n"
            f"⛔ TF-  : {', '.join(inactifs)}"
        )

    elif cmd == "/pause":
        profile["paused"] = True
        msg = "⏸ Tes notifications sont <b>suspendues</b>\n/reprendre pour réactiver"

    elif cmd == "/reprendre":
        profile["paused"] = False
        msg = f"✅ Tes notifications sont <b>réactivées</b>\nMode : {profile['mode'].upper()}"

    elif cmd == "/status":
        tf_on = [k for k,v in profile["tf_custom"].items() if v]
        etat  = "⏸ PAUSE" if profile["paused"] else "✅ ACTIF"
        msg = (
            f"🤖 <b>Ton profil FibLab Robot</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"État   : {etat}\n"
            f"Mode   : <b>{profile['mode'].upper()}</b>\n"
            f"TF+    : {', '.join(tf_on) if tf_on else 'aucun'}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Alertes globales : {len(alert_history)}\n"
            f"🥇 XAU : {len(histories['xau'])}\n"
            f"💎 SOL : {len(histories['solana'])}\n"
            f"₿ BTC  : {len(histories['btc'])}\n"
            f"🇩🇪 DAX: {len(histories['dax'])}\n"
            f"📈 STK : {len(histories['stocks'])}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"/mode swing|scalp|both\n"
            f"/tf_on 72 | /tf_off 72 | /tf_status\n"
            f"/pause | /reprendre"
        )

    elif cmd in ("/derniere","/xau","/solana","/dax","/btc","/stocks"):
        key    = cmd[1:] if cmd[1:] in histories else None
        hist   = histories[key] if key else alert_history
        labels = {"xau":"🥇 XAU","solana":"💎 Solana","dax":"🇩🇪 DAX","btc":"₿ BTC","stocks":"📈 Stocks"}
        prefix = labels.get(key, "📊 Toutes")
        if hist:
            a  = hist[0]
            sc = {"score":a.get("score",0),"level":a.get("level",""),"emoji":a.get("emoji",""),"details":a.get("details",[])}
            msg = f"🔁 <b>Dernière {prefix} :</b>\n\n" + format_telegram_message(a, sc, profile)
        else:
            msg = f"📭 Aucune alerte {prefix} pour l'instant."

    else:
        msg = (
            "🤖 <b>Commandes disponibles :</b>\n\n"
            "/status → ton profil\n"
            "/mode swing | scalp | both\n"
            "/tf_on 72 | /tf_off 72\n"
            "/tf_status\n"
            "/pause | /reprendre\n"
            "/derniere | /xau | /solana\n"
            "/btc | /dax | /stocks"
        )

    send_telegram(msg, chat_id)

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    raw = request.get_data(as_text=True).strip()
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            raw  = data.get("message", data.get("text", raw))
        except Exception:
            pass

    print(f"[WEBHOOK] Reçu : {raw[:100]}")
    if not raw:
        return jsonify({"error":"empty body"}), 400

    parsed  = parse_fiblab_message(raw)
    scoring = compute_score(parsed)
    entry   = {**parsed, **scoring}

    alert_history.appendleft(entry)
    group = get_asset_group(parsed.get("asset") or "")
    if group and group in histories:
        histories[group].appendleft(entry)

    if robot_state["paused"]:
        return jsonify({"status":"paused"}), 200

    results = {}
    for user_id in [TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_2]:
        if not user_id: continue
        profile = get_profile(user_id)
        if profile["paused"]: continue

        # Frère reçoit PRIORITAIRES uniquement
        if user_id == TELEGRAM_CHAT_ID_2 and scoring["level"] != "PRIORITAIRE":
            continue

        notify, reason = should_notify(parsed, scoring, profile)
        if not notify:
            results[user_id] = f"filtré: {reason}"
            continue

        tg_msg = format_telegram_message(parsed, scoring, profile)
        sent   = send_telegram(tg_msg, user_id)
        results[user_id] = "✅" if sent else "❌"

    print(f"[WEBHOOK] {scoring['level']} Score={scoring['score']} TF={parsed.get('timeframe')} Group={group} {results}")
    return jsonify({"status":"ok","scoring":scoring,"group":group,"results":results}), 200


@app.route("/telegram_update", methods=["POST"])
def telegram_update():
    data    = request.get_json(silent=True) or {}
    message = data.get("message", {})
    text    = message.get("text","")
    chat_id = str(message.get("chat",{}).get("id",""))
    allowed = {TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_2}
    if chat_id not in allowed:
        return jsonify({"status":"unauthorized"}), 403
    if text.startswith("/"):
        handle_telegram_command(text, chat_id)
    return jsonify({"status":"ok"}), 200


@app.route("/status", methods=["GET"])
def status():
    profiles_summary = {uid: {"mode": p["mode"], "paused": p["paused"]}
                        for uid, p in user_profiles.items()}
    return jsonify({
        "status": "paused" if robot_state["paused"] else "running",
        "alerts_total": len(alert_history),
        **{f"alerts_{g}": len(h) for g,h in histories.items()},
        "user_profiles": profiles_summary,
    })

@app.route("/",       methods=["GET"])
def dashboard_all():
    return render_template("dashboard.html", alerts=list(alert_history), page="all",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/xau",    methods=["GET"])
def dashboard_xau():
    return render_template("dashboard.html", alerts=list(histories["xau"]), page="xau",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/solana", methods=["GET"])
def dashboard_solana():
    return render_template("dashboard.html", alerts=list(histories["solana"]), page="solana",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/dax",    methods=["GET"])
def dashboard_dax():
    return render_template("dashboard.html", alerts=list(histories["dax"]), page="dax",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/btc",    methods=["GET"])
def dashboard_btc():
    return render_template("dashboard.html", alerts=list(histories["btc"]), page="btc",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/stocks", methods=["GET"])
def dashboard_stocks():
    return render_template("dashboard.html", alerts=list(histories["stocks"]), page="stocks",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/levels", methods=["GET"])
def levels():
    return jsonify(list(alert_history))

def _test(fake: str):
    parsed  = parse_fiblab_message(fake)
    scoring = compute_score(parsed)
    msg     = format_telegram_message(parsed, scoring, get_profile(TELEGRAM_CHAT_ID))
    sent_charlie = send_telegram(msg, TELEGRAM_CHAT_ID)
    sent_frere   = send_telegram(msg, TELEGRAM_CHAT_ID_2) if TELEGRAM_CHAT_ID_2 else False
    return jsonify({"telegram_charlie":sent_charlie,"telegram_frere":sent_frere,
                    "frere_configured":bool(TELEGRAM_CHAT_ID_2),"scoring":scoring})

@app.route("/test",        methods=["GET"])
def test_xau():    return _test("Origin First Touch — XAUUSD H4 | Side: Support | Price: 3325.00 | Scope: Pure")
@app.route("/test_solana", methods=["GET"])
def test_solana(): return _test("Origin First Touch — SOLUSDT.P H4 | Side: Support | Price: 142.50 | Scope: Pure")
@app.route("/test_dax",    methods=["GET"])
def test_dax():    return _test("Broken First Touch — DE30EUR H4 | Side: Resistance | Price: 24850.00 | Scope: Pure")
@app.route("/test_btc",    methods=["GET"])
def test_btc():    return _test("Origin First Touch — BTCUSDT.P H4 | Side: Support | Price: 98500.00 | Scope: Pure")
@app.route("/test_stocks", methods=["GET"])
def test_stocks(): return _test("Origin First Touch — TSLA H4 | Side: Support | Price: 285.00 | Scope: Pure")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)"""
╔══════════════════════════════════════════════════════════════╗
║         FIBLAB ROBOT — Webhook Trading Server                ║
║         Charlie Joe 1972 — Juin 2026                         ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from collections import deque

app = Flask(__name__)

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
TELEGRAM_TOKEN     = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_CHAT_ID_2 = os.environ.get("TELEGRAM_CHAT_ID_2", "")

# ─────────────────────────────────────────────
# PROFILS UTILISATEURS — indépendants par chat_id
# ─────────────────────────────────────────────
def default_profile():
    return {
        "paused": False,
        "mode": "swing",
        "tf_custom": {"72":False,"90":False,"96":False,"144":False,"160":False,"288":False}
    }

user_profiles = {}

def get_profile(chat_id: str) -> dict:
    if not chat_id: return default_profile()
    if chat_id not in user_profiles:
        user_profiles[chat_id] = default_profile()
    return user_profiles[chat_id]

# État admin global (pause totale)
robot_state = {"paused": False}

# ─────────────────────────────────────────────
# ASSETS
# ─────────────────────────────────────────────
ASSET_GROUPS = {
    "xau":    {"XAUUSD","XAU/USD","GOLD","GC1!","MGC1!"},
    "dax":    {"DE30EUR","GER30","DAX40","FDAX1!","DE30","GER40","DAX"},
    "solana": {"SOLUSDT","SOL/USD","SOLUSDT.P","SOLUSD"},
    "btc":    {"BTCUSDT","BTC/USD","BTCUSDT.P","BTCUSD","BTCUSDTP"},
    "stocks": {"TSLA","HOOD","CELH","TTD","PLTR","AMZN","NVDA","AAPL","META","GOOGL","MSFT","SOFI"},
}

ASSET_META = {
    "xau":    {"label":"XAU/USD",  "emoji":"🥇","tv":"https://www.tradingview.com/chart/?symbol=OANDA:XAUUSD"},
    "dax":    {"label":"DAX",      "emoji":"🇩🇪","tv":"https://www.tradingview.com/chart/?symbol=OANDA:DE30EUR"},
    "solana": {"label":"SOLANA",   "emoji":"💎","tv":"https://www.tradingview.com/chart/?symbol=BITGET:SOLUSDT.P"},
    "btc":    {"label":"BITCOIN",  "emoji":"₿", "tv":"https://www.tradingview.com/chart/?symbol=BITGET:BTCUSDT.P"},
    "stocks": {"label":"STOCKS",   "emoji":"📈","tv":"https://www.tradingview.com/chart/?symbol=NASDAQ:"},
}

def get_asset_group(asset: str) -> str:
    if not asset: return None
    a = asset.upper().replace("-","").replace(".","").replace("/","")
    for group, assets in ASSET_GROUPS.items():
        for ref in assets:
            if a == ref.upper().replace("-","").replace(".","").replace("/",""):
                return group
    return None

def get_tv_link(asset: str, group: str) -> str:
    if not group: return ""
    meta = ASSET_META.get(group, {})
    if group == "stocks" and asset:
        return f"https://www.tradingview.com/chart/?symbol=NASDAQ:{asset}"
    return meta.get("tv","")

# Historiques
alert_history = deque(maxlen=200)
histories = {g: deque(maxlen=100) for g in ASSET_GROUPS}

# ─────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────
def normalize_timeframe(tf: str) -> str:
    numeric_map = {
        "1":"M1","2":"M2","3":"M3","4":"M4","5":"M5","10":"M10",
        "15":"M15","30":"M30","45":"M45",
        "60":"H1","120":"H2","180":"H3","240":"H4",
        "360":"H6","480":"H8","720":"H12",
        "1440":"D1","10080":"W1","43200":"MN",
        "72":"72m","90":"90m","96":"96m",
        "144":"144m","160":"160m","288":"288m",
    }
    return numeric_map.get(tf, tf)

def parse_fiblab_message(raw: str) -> dict:
    result = {
        "raw": raw.strip(), "type":None, "asset":None,
        "timeframe":None, "side":None, "price":None,
        "scope":None, "timestamp": datetime.utcnow().isoformat(),
    }
    if "ATR PROXIMITY" in raw.upper():
        result["type"] = "ATR Proximity"
        m = re.search(r'TF:\s*([^\n\r|]+)', raw, re.IGNORECASE)
        if m: result["timeframe"] = normalize_timeframe(m.group(1).strip().upper())
        m = re.search(r'Side:\s*(Support|Resistance)', raw, re.IGNORECASE)
        if m: result["side"] = m.group(1).capitalize()
        m = re.search(r'Origin entry nearby:\s*([\d.]+)', raw, re.IGNORECASE)
        if m: result["price"] = float(m.group(1))
        result["scope"] = "Pure"
        return result

    if "—" in raw:
        parts = raw.split("—", 1)
        result["type"] = parts[0].strip()
        rest = parts[1].strip()
    else:
        rest = raw

    asset_tf = re.search(
        r'([A-Z0-9./]+)\s+([0-9]+[SMHD]?|[HMD][0-9]+|Daily|Weekly|Monthly)',
        rest, re.IGNORECASE
    )
    if asset_tf:
        result["asset"] = asset_tf.group(1).upper()
        result["timeframe"] = normalize_timeframe(asset_tf.group(2).upper())

    m = re.search(r'Side:\s*(Support|Resistance)', rest, re.IGNORECASE)
    if m: result["side"] = m.group(1).capitalize()
    m = re.search(r'Price:\s*([\d.]+)', rest)
    if m: result["price"] = float(m.group(1))
    m = re.search(r'Scope:\s*(Pure|Non-Pure)', rest, re.IGNORECASE)
    if m: result["scope"] = m.group(1)
    return result

# ─────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────
TF_WEIGHT = {
    "M1":0,"M2":0,"M3":0,"M4":0,"M5":1,"M10":1,"M15":1,"M30":1,"M45":1,
    "H1":2,"H2":2,"H3":2,
    "H4":3,"H6":3,"H8":3,"H12":3,
    "D1":4,"1D":4,"D":4,"DAILY":4,
    "W1":4,"1W":4,"W":4,"WEEKLY":4,"MN":4,"MONTHLY":4,
    "72m":1,"90m":1,"96m":1,"144m":2,"160m":2,"288m":2,
}

TYPE_SCORES = {
    "origin untouched":5,"origin first touch":4,
    "broken origin first touch":4,"broken first touch":3,
    "break first touch":3,"atr proximity":3,
    "break created":2,"origin broken":2,"bsut created":2,
    "origin touched":1,
}

def compute_score(parsed: dict) -> dict:
    score, details = 0, []
    alert_type = (parsed.get("type") or "").lower()
    tf    = (parsed.get("timeframe") or "").upper()
    scope = (parsed.get("scope") or "").lower()

    for key, val in TYPE_SCORES.items():
        if key in alert_type:
            score += val
            details.append(f"Type '{parsed['type']}' → +{val}")
            break

    if scope == "pure":
        score += 2
        details.append("Scope Pure → +2")

    tf_score = TF_WEIGHT.get(tf, TF_WEIGHT.get(tf.lower(), 0))
    if tf_score > 0:
        score += tf_score
        details.append(f"Timeframe {tf} → +{tf_score}")

    if "first touch" in alert_type:
        score += 2
        details.append("Première visite (First Touch) → +2")

    if score >= 8:   level, emoji = "PRIORITAIRE","🔴"
    elif score >= 5: level, emoji = "SECONDAIRE", "⚠️"
    else:            level, emoji = "INFO",        "📊"

    return {"score":score,"level":level,"emoji":emoji,"details":details}

# ─────────────────────────────────────────────
# FILTRES — basés sur le profil utilisateur
# ─────────────────────────────────────────────
TF_SWING  = {"H4","H6","H8","H12","D1","D2","D3","D4","D5","D6","D7",
             "W1","MN","1D","2D","3D","4D","5D","6D","7D","1W","4H","8H","12H"}
TF_SCALP  = {"M1","M2","M3","M4","M5","M10","M15","M30","M45","H1","H2","H3","H4","4H"}
TF_CUSTOM = {"72m","90m","96m","144m","160m","288m"}
TF_DAILY  = {"D1","D2","D3","D4","D5","D6","D7","1D","2D","3D","4D","5D","6D","7D","W1","MN","1W"}

TYPES_ALWAYS     = {"origin first touch","origin untouched","atr proximity",
                    "break first touch","broken first touch","broken origin first touch"}
TYPES_DAILY_ONLY = {"origin touched"}
TYPES_SCORE_MIN  = {"bsut created": 6}
TYPES_IGNORED    = {"break created"}

def should_notify(parsed: dict, scoring: dict, profile: dict) -> tuple:
    alert_type = (parsed.get("type") or "").lower()
    tf         = (parsed.get("timeframe") or "").upper()
    tf_lower   = tf.lower()
    mode       = profile["mode"]

    if tf_lower in TF_CUSTOM:
        key = tf_lower.replace("m","")
        if not profile["tf_custom"].get(key, False):
            return False, f"TF custom '{tf}' désactivé"
    elif mode == "swing" and tf not in TF_SWING:
        return False, f"Mode SWING : TF '{tf}' ignoré"
    elif mode == "scalp" and tf not in TF_SCALP:
        return False, f"Mode SCALP : TF '{tf}' ignoré"
    elif mode == "both" and tf not in TF_SWING | TF_SCALP:
        return False, f"TF '{tf}' non reconnu"

    for ignored in TYPES_IGNORED:
        if ignored in alert_type:
            return False, f"Type ignoré"

    for t, min_score in TYPES_SCORE_MIN.items():
        if t in alert_type:
            if scoring["score"] < min_score:
                return False, f"BSUT score {scoring['score']} < {min_score}"
            return True, "ok"

    for t in TYPES_DAILY_ONLY:
        if t in alert_type:
            if tf not in TF_DAILY:
                return False, f"Origin Touched nécessite Daily+"
            return True, "ok"

    for t in TYPES_ALWAYS:
        if t in alert_type:
            return True, "ok"

    if scoring["score"] >= 5:
        return True, "ok"

    return False, f"Score insuffisant"

# ─────────────────────────────────────────────
# TELEGRAM
# ─────────────────────────────────────────────
def send_telegram(message: str, chat_id: str = None):
    if not TELEGRAM_TOKEN: return False
    target = chat_id or TELEGRAM_CHAT_ID
    if not target: return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": target, "text": message, "parse_mode": "HTML"},
            timeout=10
        )
        return r.status_code == 200
    except Exception as e:
        print(f"[TELEGRAM] Erreur : {e}")
        return False

def format_telegram_message(parsed: dict, scoring: dict, profile: dict = None) -> str:
    asset   = parsed.get("asset") or None
    group   = get_asset_group(asset) if asset else None
    meta    = ASSET_META.get(group, {"emoji":"📡","label":asset or "?"})
    is_atr  = "atr" in (parsed.get("type") or "").lower()
    tv_link = get_tv_link(asset, group)
    mode    = (profile or {}).get("mode","swing")

    side_emoji    = "🟢" if parsed.get("side") == "Support" else "🔴"
    scope_tag     = "✅ Pure" if parsed.get("scope") == "Pure" else "⬜ Non-Pure"
    asset_display = f"{meta['emoji']} {asset}" if asset else f"{meta['emoji']} voir chart"
    action = (
        "→ Surveille M1 maintenant\n→ Setup <b>LONG</b> potentiel\n→ SL visé : 5-10 pts"
        if parsed.get("side") == "Support" else
        "→ Surveille M1 maintenant\n→ Setup <b>SHORT</b> potentiel\n→ SL visé : 5-10 pts"
    )

    msg = (
        f"{scoring['emoji']} <b>ALERTE {scoring['level']} — Score {scoring['score']}/15</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Asset    : <b>{asset_display}</b>\n"
        f"Niveau   : <b>{parsed.get('price','?')}</b>\n"
        f"Type     : {'📡 ' if is_atr else ''}{parsed.get('type','?')}\n"
        f"TF       : {parsed.get('timeframe','?')}\n"
        f"Side     : {side_emoji} {parsed.get('side','?')}\n"
        f"Scope    : {scope_tag}\n"
        f"Mode     : {mode.upper()}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Scoring :\n"
    )
    for d in scoring["details"]:
        msg += f"  • {d}\n"

    tv_line = f"\n📈 <a href='{tv_link}'>Ouvrir le chart</a>" if tv_link else ""
    msg += (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Action :\n{action}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {parsed.get('timestamp','')[:19].replace('T',' ')} UTC"
        f"{tv_line}"
    )
    return msg

# ─────────────────────────────────────────────
# COMMANDES TELEGRAM
# ─────────────────────────────────────────────
def handle_telegram_command(text: str, chat_id: str):
    parts   = text.strip().lower().split()
    cmd     = parts[0]
    arg     = parts[1] if len(parts) > 1 else ""
    profile = get_profile(chat_id)

    if cmd == "/mode":
        if arg in ("swing","scalp","both"):
            profile["mode"] = arg
            labels = {"swing":"🔵 SWING (H4+)","scalp":"⚡ SCALP (M1→H4)","both":"🌐 BOTH (tout)"}
            msg = f"✅ Ton mode → <b>{labels[arg]}</b>\n(ne change rien pour les autres utilisateurs)"
        else:
            msg = "Usage : /mode swing | /mode scalp | /mode both"

    elif cmd == "/tf_on":
        if arg in profile["tf_custom"]:
            profile["tf_custom"][arg] = True
            msg = f"✅ TF <b>{arg}m</b> activé pour toi"
        else:
            msg = f"TF '{arg}' inconnu. Disponibles : 72 90 96 144 160 288"

    elif cmd == "/tf_off":
        if arg in profile["tf_custom"]:
            profile["tf_custom"][arg] = False
            msg = f"⛔ TF <b>{arg}m</b> désactivé pour toi"
        else:
            msg = f"TF '{arg}' inconnu. Disponibles : 72 90 96 144 160 288"

    elif cmd == "/tf_status":
        actifs   = [k for k,v in profile["tf_custom"].items() if v]
        inactifs = [k for k,v in profile["tf_custom"].items() if not v]
        msg = (
            f"📊 <b>Ton profil TF</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Mode    : <b>{profile['mode'].upper()}</b>\n"
            f"✅ TF+  : {', '.join(actifs) if actifs else 'aucun'}\n"
            f"⛔ TF-  : {', '.join(inactifs)}"
        )

    elif cmd == "/pause":
        profile["paused"] = True
        msg = "⏸ Tes notifications sont <b>suspendues</b>\n/reprendre pour réactiver"

    elif cmd == "/reprendre":
        profile["paused"] = False
        msg = f"✅ Tes notifications sont <b>réactivées</b>\nMode : {profile['mode'].upper()}"

    elif cmd == "/status":
        tf_on = [k for k,v in profile["tf_custom"].items() if v]
        etat  = "⏸ PAUSE" if profile["paused"] else "✅ ACTIF"
        msg = (
            f"🤖 <b>Ton profil FibLab Robot</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"État   : {etat}\n"
            f"Mode   : <b>{profile['mode'].upper()}</b>\n"
            f"TF+    : {', '.join(tf_on) if tf_on else 'aucun'}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Alertes globales : {len(alert_history)}\n"
            f"🥇 XAU : {len(histories['xau'])}\n"
            f"💎 SOL : {len(histories['solana'])}\n"
            f"₿ BTC  : {len(histories['btc'])}\n"
            f"🇩🇪 DAX: {len(histories['dax'])}\n"
            f"📈 STK : {len(histories['stocks'])}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"/mode swing|scalp|both\n"
            f"/tf_on 72 | /tf_off 72 | /tf_status\n"
            f"/pause | /reprendre"
        )

    elif cmd in ("/derniere","/xau","/solana","/dax","/btc","/stocks"):
        key    = cmd[1:] if cmd[1:] in histories else None
        hist   = histories[key] if key else alert_history
        labels = {"xau":"🥇 XAU","solana":"💎 Solana","dax":"🇩🇪 DAX","btc":"₿ BTC","stocks":"📈 Stocks"}
        prefix = labels.get(key, "📊 Toutes")
        if hist:
            a  = hist[0]
            sc = {"score":a.get("score",0),"level":a.get("level",""),"emoji":a.get("emoji",""),"details":a.get("details",[])}
            msg = f"🔁 <b>Dernière {prefix} :</b>\n\n" + format_telegram_message(a, sc, profile)
        else:
            msg = f"📭 Aucune alerte {prefix} pour l'instant."

    else:
        msg = (
            "🤖 <b>Commandes disponibles :</b>\n\n"
            "/status → ton profil\n"
            "/mode swing | scalp | both\n"
            "/tf_on 72 | /tf_off 72\n"
            "/tf_status\n"
            "/pause | /reprendre\n"
            "/derniere | /xau | /solana\n"
            "/btc | /dax | /stocks"
        )

    send_telegram(msg, chat_id)

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    raw = request.get_data(as_text=True).strip()
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            raw  = data.get("message", data.get("text", raw))
        except Exception:
            pass

    print(f"[WEBHOOK] Reçu : {raw[:100]}")
    if not raw:
        return jsonify({"error":"empty body"}), 400

    parsed  = parse_fiblab_message(raw)
    scoring = compute_score(parsed)
    entry   = {**parsed, **scoring}

    alert_history.appendleft(entry)
    group = get_asset_group(parsed.get("asset") or "")
    if group and group in histories:
        histories[group].appendleft(entry)

    if robot_state["paused"]:
        return jsonify({"status":"paused"}), 200

    results = {}
    for user_id in [TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_2]:
        if not user_id: continue
        profile = get_profile(user_id)
        if profile["paused"]: continue

        # Frère reçoit PRIORITAIRES uniquement
        if user_id == TELEGRAM_CHAT_ID_2 and scoring["level"] != "PRIORITAIRE":
            continue

        notify, reason = should_notify(parsed, scoring, profile)
        if not notify:
            results[user_id] = f"filtré: {reason}"
            continue

        tg_msg = format_telegram_message(parsed, scoring, profile)
        sent   = send_telegram(tg_msg, user_id)
        results[user_id] = "✅" if sent else "❌"

    print(f"[WEBHOOK] {scoring['level']} Score={scoring['score']} TF={parsed.get('timeframe')} Group={group} {results}")
    return jsonify({"status":"ok","scoring":scoring,"group":group,"results":results}), 200


@app.route("/telegram_update", methods=["POST"])
def telegram_update():
    data    = request.get_json(silent=True) or {}
    message = data.get("message", {})
    text    = message.get("text","")
    chat_id = str(message.get("chat",{}).get("id",""))
    allowed = {TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_2}
    if chat_id not in allowed:
        return jsonify({"status":"unauthorized"}), 403
    if text.startswith("/"):
        handle_telegram_command(text, chat_id)
    return jsonify({"status":"ok"}), 200


@app.route("/status", methods=["GET"])
def status():
    profiles_summary = {uid: {"mode": p["mode"], "paused": p["paused"]}
                        for uid, p in user_profiles.items()}
    return jsonify({
        "status": "paused" if robot_state["paused"] else "running",
        "alerts_total": len(alert_history),
        **{f"alerts_{g}": len(h) for g,h in histories.items()},
        "user_profiles": profiles_summary,
    })

@app.route("/",       methods=["GET"])
def dashboard_all():
    return render_template("dashboard.html", alerts=list(alert_history), page="all",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/xau",    methods=["GET"])
def dashboard_xau():
    return render_template("dashboard.html", alerts=list(histories["xau"]), page="xau",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/solana", methods=["GET"])
def dashboard_solana():
    return render_template("dashboard.html", alerts=list(histories["solana"]), page="solana",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/dax",    methods=["GET"])
def dashboard_dax():
    return render_template("dashboard.html", alerts=list(histories["dax"]), page="dax",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/btc",    methods=["GET"])
def dashboard_btc():
    return render_template("dashboard.html", alerts=list(histories["btc"]), page="btc",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/stocks", methods=["GET"])
def dashboard_stocks():
    return render_template("dashboard.html", alerts=list(histories["stocks"]), page="stocks",
        counts={g:len(h) for g,h in histories.items()})
@app.route("/levels", methods=["GET"])
def levels():
    return jsonify(list(alert_history))

def _test(fake: str):
    parsed  = parse_fiblab_message(fake)
    scoring = compute_score(parsed)
    msg     = format_telegram_message(parsed, scoring, get_profile(TELEGRAM_CHAT_ID))
    sent_charlie = send_telegram(msg, TELEGRAM_CHAT_ID)
    sent_frere   = send_telegram(msg, TELEGRAM_CHAT_ID_2) if TELEGRAM_CHAT_ID_2 else False
    return jsonify({"telegram_charlie":sent_charlie,"telegram_frere":sent_frere,
                    "frere_configured":bool(TELEGRAM_CHAT_ID_2),"scoring":scoring})

@app.route("/test",        methods=["GET"])
def test_xau():    return _test("Origin First Touch — XAUUSD H4 | Side: Support | Price: 3325.00 | Scope: Pure")
@app.route("/test_solana", methods=["GET"])
def test_solana(): return _test("Origin First Touch — SOLUSDT.P H4 | Side: Support | Price: 142.50 | Scope: Pure")
@app.route("/test_dax",    methods=["GET"])
def test_dax():    return _test("Broken First Touch — DE30EUR H4 | Side: Resistance | Price: 24850.00 | Scope: Pure")
@app.route("/test_btc",    methods=["GET"])
def test_btc():    return _test("Origin First Touch — BTCUSDT.P H4 | Side: Support | Price: 98500.00 | Scope: Pure")
@app.route("/test_stocks", methods=["GET"])
def test_stocks(): return _test("Origin First Touch — TSLA H4 | Side: Support | Price: 285.00 | Scope: Pure")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
