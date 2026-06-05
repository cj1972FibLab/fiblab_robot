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
# CONFIGURATION — Variables Railway
# ─────────────────────────────────────────────
TELEGRAM_TOKEN     = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")      # Charlie — toutes alertes
TELEGRAM_CHAT_ID_2 = os.environ.get("TELEGRAM_CHAT_ID_2", "")   # Frère — PRIORITAIRES uniquement

# État global
robot_state = {"paused": False}

# ─────────────────────────────────────────────
# ASSETS PAR CATÉGORIE
# ─────────────────────────────────────────────
ASSET_GROUPS = {
    "xau":    {"XAUUSD", "XAU/USD", "GOLD", "GC1!", "MGC1!"},
    "solana": {"SOLUSDT", "SOL/USD", "SOLUSDT.P", "SOLUSD"},
    "dax":    {"DE30EUR", "GER30", "DAX40", "FDAX1!", "DE30", "GER40", "DAX"},
}

ASSET_META = {
    "xau":    {"label": "XAU/USD",  "emoji": "🥇", "color": "#f5a623", "tv": "https://www.tradingview.com/chart/?symbol=OANDA:XAUUSD"},
    "solana": {"label": "SOLANA",   "emoji": "💎", "color": "#a78bfa", "tv": "https://www.tradingview.com/chart/?symbol=BITGET:SOLUSDT.P"},
    "dax":    {"label": "DAX",      "emoji": "🇩🇪", "color": "#3fb950", "tv": "https://www.tradingview.com/chart/?symbol=OANDA:DE30EUR"},
}

def get_asset_group(asset: str) -> str:
    """Retourne la catégorie d'un asset ou None"""
    if not asset:
        return None
    a = asset.upper().replace("-", "").replace(".", "").replace("/", "")
    for group, assets in ASSET_GROUPS.items():
        for ref in assets:
            if a == ref.upper().replace("-","").replace(".","").replace("/",""):
                return group
    return None

# Historiques
alert_history = deque(maxlen=200)
histories = {
    "xau":    deque(maxlen=100),
    "solana": deque(maxlen=100),
    "dax":    deque(maxlen=100),
}


# ─────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────
def normalize_timeframe(tf: str) -> str:
    numeric_map = {
        "1": "M1", "3": "M3", "5": "M5", "10": "M10",
        "15": "M15", "30": "M30", "45": "M45",
        "60": "H1", "120": "H2", "180": "H3", "240": "H4",
        "360": "H6", "480": "H8", "720": "H12",
        "1440": "D1", "10080": "W1", "43200": "MN",
    }
    return numeric_map.get(tf, tf)


def parse_fiblab_message(raw: str) -> dict:
    result = {
        "raw": raw.strip(),
        "type": None, "asset": None, "timeframe": None,
        "side": None, "price": None, "scope": None,
        "timestamp": datetime.utcnow().isoformat(),
    }
    # ── Format ATR PROXIMITY (multiligne, pas de "—") ──
    # Origin ATR PROXIMITY\nTF: 2D\nSide: Support\nOrigin entry nearby: 55.555\nDistance: 3.56x ATR\nATR: 5.2
    if raw.startswith("Origin ATR PROXIMITY") or raw.startswith("ATR PROXIMITY"):
        result["type"] = "ATR Proximity"

        m = re.search(r'TF:\s*([^\n\r|]+)', raw, re.IGNORECASE)
        if m:
            tf_raw = m.group(1).strip().upper()
            result["timeframe"] = normalize_timeframe(tf_raw)

        m = re.search(r'Side:\s*(Support|Resistance)', raw, re.IGNORECASE)
        if m: result["side"] = m.group(1).capitalize()

        # Prix = "Origin entry nearby"
        m = re.search(r'Origin entry nearby:\s*([\d.]+)', raw, re.IGNORECASE)
        if m: result["price"] = float(m.group(1))

        # Pas d'asset dans le message ATR → on le laisse None
        # L'asset sera déduit du chart TradingView si possible
        result["scope"] = "Pure"   # ATR Proximity = toujours sur Origin Untouched Pure
        return result

    # ── Format standard (avec "—") ──
    if "—" in raw:
        parts = raw.split("—", 1)
        result["type"] = parts[0].strip()
        rest = parts[1].strip()
    else:
        rest = raw

    asset_tf = re.search(r'([A-Z0-9./]+)\s+([0-9]+[SMHD]?|[HMD][0-9]+|Daily|Weekly|Monthly)', rest, re.IGNORECASE)
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
    "M1":0,"M3":0,"M5":0,"M10":0,"M15":0,"M30":0,"M45":0,
    "1M":0,"3M":0,"5M":0,"15M":0,"30M":0,"30S":0,"1S":0,
    "H1":1,"H2":1,"1H":1,"2H":1,
    "H3":2,"H4":2,"H6":2,"H8":2,"H12":2,"4H":2,"8H":2,"12H":2,
    "D1":3,"1D":3,"D":3,"DAILY":3,
    "W1":3,"1W":3,"W":3,"WEEKLY":3,"MN":3,"MONTHLY":3,
}

TYPE_SCORES = {
    "origin untouched":5, "origin first touch":4,
    "broken origin first touch":4, "broken first touch":3,
    "break first touch":3, "break created":2,
    "origin broken":2, "bsut created":2,
    "atr proximity":3, "origin touched":1,
}

def compute_score(parsed: dict) -> dict:
    score, details = 0, []
    alert_type = (parsed.get("type") or "").lower()
    tf = (parsed.get("timeframe") or "").upper()
    scope = (parsed.get("scope") or "").lower()

    for key, val in TYPE_SCORES.items():
        if key in alert_type:
            score += val
            details.append(f"Type '{parsed['type']}' → +{val}")
            break

    if scope == "pure":
        score += 2
        details.append("Scope Pure → +2")

    tf_score = TF_WEIGHT.get(tf, 0)
    if tf_score > 0:
        score += tf_score
        details.append(f"Timeframe {tf} → +{tf_score}")

    if "first touch" in alert_type:
        score += 2
        details.append("Première visite (First Touch) → +2")

    if score >= 8:   level, emoji = "PRIORITAIRE", "🔴"
    elif score >= 5: level, emoji = "SECONDAIRE",  "⚠️"
    else:            level, emoji = "INFO",         "📊"

    return {"score": score, "level": level, "emoji": emoji, "details": details}


# ─────────────────────────────────────────────
# FILTRES ALERTES
# ─────────────────────────────────────────────

# TF minimum pour recevoir une notification
TF_MINIMUM = {"H4","H6","H8","H12","D1","D2","D3","D4","D5","D6","D7","W1","MN",
               "4H","8H","12H","1D","2D","3D","4D","5D","6D","7D","1W"}

# Types toujours notifiés (H4+)
TYPES_ALWAYS = {
    "origin first touch", "origin untouched",
    "atr proximity",
    "break first touch", "broken first touch",
    "broken origin first touch",
}

# Types notifiés seulement si Daily+
TF_DAILY = {"D1","D2","D3","D4","D5","D6","D7","1D","2D","3D","4D","5D","6D","7D","W1","MN","1W"}
TYPES_DAILY_ONLY = {"origin touched"}

# Types notifiés seulement si score 6+
TYPES_SCORE_MIN = {"bsut created": 6}

# Types toujours ignorés
TYPES_IGNORED = {"break created"}

def should_notify(parsed: dict, scoring: dict) -> tuple[bool, str]:
    """Retourne (notifier, raison_si_non)"""
    alert_type = (parsed.get("type") or "").lower()
    tf = (parsed.get("timeframe") or "").upper()

    # 1. TF minimum H4
    if tf not in TF_MINIMUM:
        return False, f"TF '{tf}' < H4 — ignoré"

    # 2. Types ignorés
    for ignored in TYPES_IGNORED:
        if ignored in alert_type:
            return False, f"Type '{alert_type}' ignoré"

    # 3. Types score minimum
    for t, min_score in TYPES_SCORE_MIN.items():
        if t in alert_type:
            if scoring["score"] < min_score:
                return False, f"Type '{alert_type}' score {scoring['score']} < {min_score}"
            return True, "ok"

    # 4. Types Daily+ seulement
    for t in TYPES_DAILY_ONLY:
        if t in alert_type:
            if tf not in TF_DAILY:
                return False, f"Type '{alert_type}' nécessite Daily+ (TF={tf})"
            return True, "ok"

    # 5. Types toujours notifiés (H4+)
    for t in TYPES_ALWAYS:
        if t in alert_type:
            return True, "ok"

    # 6. Autres types non listés → on notifie si score 5+
    if scoring["score"] >= 5:
        return True, "ok"

    return False, f"Score {scoring['score']} insuffisant"


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


def format_telegram_message(parsed: dict, scoring: dict) -> str:
    asset  = parsed.get("asset") or None
    group  = get_asset_group(asset) if asset else None
    meta   = ASSET_META.get(group, {"emoji": "📡", "label": asset or "?"})
    is_atr = "atr" in (parsed.get("type") or "").lower()

    side_emoji = "🟢" if parsed.get("side") == "Support" else "🔴"
    scope_tag  = "✅ Pure" if parsed.get("scope") == "Pure" else "⬜ Non-Pure"
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
        f"Niveau   : <b>{parsed.get('price', '?')}</b>\n"
        f"Type     : {'📡 ' if is_atr else ''}{parsed.get('type', '?')}\n"
        f"TF       : {parsed.get('timeframe', '?')}\n"
        f"Side     : {side_emoji} {parsed.get('side', '?')}\n"
        f"Scope    : {scope_tag}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Scoring :\n"
    )
    for d in scoring["details"]:
        msg += f"  • {d}\n"

    # Lien TradingView
    tv_link = meta.get("tv", "")
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
    cmd = text.strip().lower().split()[0]

    if cmd == "/status":
        etat = "⏸ EN PAUSE" if robot_state["paused"] else "✅ ACTIF"
        msg = (
            f"🤖 <b>FibLab Robot</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"État      : {etat}\n"
            f"Total     : {len(alert_history)} alertes\n"
            f"🥇 XAU    : {len(histories['xau'])}\n"
            f"💎 Solana : {len(histories['solana'])}\n"
            f"🇩🇪 DAX   : {len(histories['dax'])}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"/pause /reprendre /derniere\n"
            f"/xau /solana /dax"
        )

    elif cmd == "/pause":
        robot_state["paused"] = True
        msg = "⏸ Robot mis en <b>pause</b> — plus de notifications."

    elif cmd == "/reprendre":
        robot_state["paused"] = False
        msg = "✅ Robot <b>réactivé</b> — notifications reprises."

    elif cmd in ("/derniere", "/xau", "/solana", "/dax"):
        key = {"derniere": None, "xau": "xau", "solana": "solana", "dax": "dax"}[cmd[1:]]
        hist = histories[key] if key else alert_history
        labels = {"xau":"🥇 XAU", "solana":"💎 Solana", "dax":"🇩🇪 DAX"}
        prefix = labels.get(key, "📊 Toutes")
        if hist:
            a = hist[0]
            sc = {"score":a.get("score",0),"level":a.get("level",""),"emoji":a.get("emoji",""),"details":a.get("details",[])}
            msg = f"🔁 <b>Dernière alerte {prefix} :</b>\n\n" + format_telegram_message(a, sc)
        else:
            msg = f"📭 Aucune alerte {prefix} pour l'instant."

    else:
        msg = (
            "🤖 <b>Commandes disponibles :</b>\n\n"
            "/status → état du robot\n"
            "/pause → suspendre\n"
            "/reprendre → réactiver\n"
            "/derniere → dernière alerte\n"
            "/xau → dernière alerte XAU\n"
            "/solana → dernière alerte SOL\n"
            "/dax → dernière alerte DAX"
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
            raw = data.get("message", data.get("text", raw))
        except Exception:
            pass

    print(f"[WEBHOOK] Reçu : {raw}")
    if not raw:
        return jsonify({"error": "empty body"}), 400

    parsed  = parse_fiblab_message(raw)
    scoring = compute_score(parsed)
    entry   = {**parsed, **scoring}

    # Historique global
    alert_history.appendleft(entry)

    # Historique par groupe
    group = get_asset_group(parsed.get("asset") or "")
    if group:
        histories[group].appendleft(entry)

    # Pause ?
    if robot_state["paused"]:
        print("[WEBHOOK] Robot en pause — pas de Telegram")
        return jsonify({"status": "paused", "parsed": parsed, "scoring": scoring}), 200

    # ── FILTRE INTELLIGENT ──
    notify, reason = should_notify(parsed, scoring)
    if not notify:
        print(f"[WEBHOOK] Filtré : {reason}")
        return jsonify({"status": "filtered", "reason": reason, "parsed": parsed}), 200

    tg_msg = format_telegram_message(parsed, scoring)

    # Charlie reçoit tout
    sent_charlie = send_telegram(tg_msg, TELEGRAM_CHAT_ID)

    # Frère reçoit les PRIORITAIRES uniquement
    sent_frere = False
    if TELEGRAM_CHAT_ID_2 and scoring["level"] == "PRIORITAIRE":
        sent_frere = send_telegram(tg_msg, TELEGRAM_CHAT_ID_2)

    print(f"[WEBHOOK] Score={scoring['score']} Level={scoring['level']} Group={group} Charlie={'✅' if sent_charlie else '❌'} Frère={'✅' if sent_frere else '❌'}")

    return jsonify({
        "status": "ok", "parsed": parsed, "scoring": scoring,
        "group": group, "telegram_charlie": sent_charlie, "telegram_frere": sent_frere,
    }), 200


@app.route("/telegram_update", methods=["POST"])
def telegram_update():
    data    = request.get_json(silent=True) or {}
    message = data.get("message", {})
    text    = message.get("text", "")
    chat_id = str(message.get("chat", {}).get("id", ""))
    allowed = {TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_2}
    if chat_id not in allowed:
        return jsonify({"status": "unauthorized"}), 403
    if text.startswith("/"):
        handle_telegram_command(text, chat_id)
    return jsonify({"status": "ok"}), 200


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "paused" if robot_state["paused"] else "running",
        "alerts_total": len(alert_history),
        "alerts_xau": len(histories["xau"]),
        "alerts_solana": len(histories["solana"]),
        "alerts_dax": len(histories["dax"]),
        "telegram_configured": bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID),
        "frere_configured": bool(TELEGRAM_CHAT_ID_2),
        "last_alert": alert_history[0]["timestamp"] if alert_history else None,
    })


@app.route("/", methods=["GET"])
def dashboard_all():
    return render_template("dashboard.html",
        alerts=list(alert_history), page="all",
        counts={"xau": len(histories["xau"]), "solana": len(histories["solana"]), "dax": len(histories["dax"])})

@app.route("/xau", methods=["GET"])
def dashboard_xau():
    return render_template("dashboard.html",
        alerts=list(histories["xau"]), page="xau",
        counts={"xau": len(histories["xau"]), "solana": len(histories["solana"]), "dax": len(histories["dax"])})

@app.route("/solana", methods=["GET"])
def dashboard_solana():
    return render_template("dashboard.html",
        alerts=list(histories["solana"]), page="solana",
        counts={"xau": len(histories["xau"]), "solana": len(histories["solana"]), "dax": len(histories["dax"])})

@app.route("/dax", methods=["GET"])
def dashboard_dax():
    return render_template("dashboard.html",
        alerts=list(histories["dax"]), page="dax",
        counts={"xau": len(histories["xau"]), "solana": len(histories["solana"]), "dax": len(histories["dax"])})

@app.route("/levels", methods=["GET"])
def levels():
    return jsonify(list(alert_history))

@app.route("/test", methods=["GET"])
def test_alert():
    fake   = "Origin First Touch — XAUUSD H4 | Side: Support | Price: 3325.00 | Scope: Pure"
    parsed = parse_fiblab_message(fake)
    scoring= compute_score(parsed)
    sent   = send_telegram(format_telegram_message(parsed, scoring), TELEGRAM_CHAT_ID)
    return jsonify({"telegram_sent": sent, "scoring": scoring})

@app.route("/test_solana", methods=["GET"])
def test_solana():
    fake   = "Origin First Touch — SOLUSDT.P H4 | Side: Support | Price: 142.50 | Scope: Pure"
    parsed = parse_fiblab_message(fake)
    scoring= compute_score(parsed)
    sent   = send_telegram(format_telegram_message(parsed, scoring), TELEGRAM_CHAT_ID)
    return jsonify({"telegram_sent": sent, "scoring": scoring})

@app.route("/test_dax", methods=["GET"])
def test_dax():
    fake   = "Broken First Touch — DE30EUR H4 | Side: Resistance | Price: 24850.00 | Scope: Pure"
    parsed = parse_fiblab_message(fake)
    scoring= compute_score(parsed)
    sent   = send_telegram(format_telegram_message(parsed, scoring), TELEGRAM_CHAT_ID)
    return jsonify({"telegram_sent": sent, "scoring": scoring})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
