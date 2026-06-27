"""
╔══════════════════════════════════════════════════════════════╗
║         FIBLAB ROBOT — Webhook Trading Server  (v2.5.0)      ║
║         Charlie Joe 1972 — Juin 2026                         ║
║                                                              ║
║  Base v2.1.0 + patch :                                       ║
║   • Scoring 6D/7D (D6/D7) — tes plus hauts TF scoraient 0    ║
║   • load_alert_history() : dashboard survit aux redéploys    ║
║   • send_telegram() avec retry + backoff (sans dépendance)   ║
║   • /db_count : preuve de persistance (COUNT réel en base)   ║
║                                                              ║
║  Hérité de v2.1.0 :                                          ║
║   • TF 2D/3D/4D pris en compte dans le scoring               ║
║   • /webhook authentifié (WEBHOOK_SECRET, query ?token=)     ║
║   • Échappement HTML des champs externes (anti-injection)    ║
║   • Killswitch admin (robot_state vivant)                    ║
║   • Persistance SQLite : profils + alertes + issues          ║
║   • Squelette d'évaluation d'issue (/outcome, /stats)        ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import html
import time
import sqlite3
import requests
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, render_template
from collections import deque

app = Flask(__name__)


def now_iso() -> str:
    """Horodatage UTC timezone-aware (remplace datetime.utcnow() déprécié)."""
    return datetime.now(timezone.utc).isoformat()


def esc(v) -> str:
    """Échappe une valeur externe avant insertion dans un message HTML Telegram."""
    return html.escape(str(v), quote=True) if v is not None else "?"


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
TELEGRAM_TOKEN     = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")      # Charlie = admin
TELEGRAM_CHAT_ID_2 = os.environ.get("TELEGRAM_CHAT_ID_2", "")   # Frère = PRIORITAIRES
WEBHOOK_SECRET     = os.environ.get("WEBHOOK_SECRET", "")        # secret partagé webhook
DB_PATH            = os.environ.get("DB_PATH", "fiblab.db")      # mettre sur un volume Railway !


def check_secret() -> bool:
    """True si le secret n'est pas configuré (ouvert) ou si le token fourni correspond."""
    if not WEBHOOK_SECRET:
        return True
    token = request.args.get("token") or request.headers.get("X-Webhook-Token", "")
    return token == WEBHOOK_SECRET


# ─────────────────────────────────────────────
# PERSISTANCE SQLite
# ─────────────────────────────────────────────
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT,
                asset     TEXT,
                grp       TEXT,
                timeframe TEXT,
                type      TEXT,
                side      TEXT,
                price     REAL,
                scope     TEXT,
                score     INTEGER,
                level     TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS outcomes (
                alert_id   INTEGER PRIMARY KEY,
                status     TEXT DEFAULT 'pending',   -- pending | win | loss | invalid
                mfe_pts    REAL,                     -- max favorable excursion (pts)
                mae_pts    REAL,                     -- max adverse excursion (pts)
                r_realized REAL,                     -- R atteint
                note       TEXT,
                updated_ts TEXT,
                FOREIGN KEY (alert_id) REFERENCES alerts(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                chat_id   TEXT PRIMARY KEY,
                mode      TEXT,
                paused    INTEGER,
                tf_custom TEXT
            )
        """)
        conn.commit()


def save_alert(parsed: dict, scoring: dict, group: str) -> int:
    """Insère l'alerte + une ligne 'pending' dans outcomes. Retourne l'id."""
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO alerts (ts,asset,grp,timeframe,type,side,price,scope,score,level) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (parsed.get("timestamp"), parsed.get("asset"), group, parsed.get("timeframe"),
             parsed.get("type"), parsed.get("side"), parsed.get("price"), parsed.get("scope"),
             scoring["score"], scoring["level"])
        )
        alert_id = cur.lastrowid
        conn.execute(
            "INSERT INTO outcomes (alert_id, status, updated_ts) VALUES (?, 'pending', ?)",
            (alert_id, now_iso())
        )
        conn.commit()
        return alert_id


def load_profiles():
    """Recharge les profils depuis SQLite au démarrage (survie aux redémarrages)."""
    try:
        with db() as conn:
            for row in conn.execute("SELECT * FROM profiles"):
                user_profiles[row["chat_id"]] = {
                    "paused":    bool(row["paused"]),
                    "mode":      row["mode"],
                    "tf_custom": json.loads(row["tf_custom"] or "{}"),
                }
    except Exception as e:
        print(f"[DB] load_profiles : {e}")


def save_profile(chat_id: str, profile: dict):
    with db() as conn:
        conn.execute(
            "INSERT INTO profiles (chat_id,mode,paused,tf_custom) VALUES (?,?,?,?) "
            "ON CONFLICT(chat_id) DO UPDATE SET "
            "mode=excluded.mode, paused=excluded.paused, tf_custom=excluded.tf_custom",
            (chat_id, profile["mode"], int(profile["paused"]), json.dumps(profile["tf_custom"]))
        )
        conn.commit()


# ─────────────────────────────────────────────
# PROFILS UTILISATEURS — indépendants par chat_id
# ─────────────────────────────────────────────
def default_profile():
    return {
        "paused": False,
        "mode": "swing",
        "tf_custom": {"72": False, "90": False, "96": False, "144": False, "160": False, "288": False},
    }


user_profiles = {}


def get_profile(chat_id: str) -> dict:
    if not chat_id:
        return default_profile()
    if chat_id not in user_profiles:
        user_profiles[chat_id] = default_profile()
    return user_profiles[chat_id]


# État admin global (killswitch) — réactivé via /killswitch
robot_state = {"paused": False}


# ─────────────────────────────────────────────
# ASSETS
# ─────────────────────────────────────────────
ASSET_GROUPS = {
    "xau":    {"XAUUSD", "XAU/USD", "GOLD", "GC1!", "MGC1!"},
    "dax":    {"DE30EUR", "GER30", "DAX40", "FDAX1!", "DE30", "GER40", "DAX"},
    "solana": {"SOLUSDT", "SOL/USD", "SOLUSDT.P", "SOLUSD"},
    "btc":    {"BTCUSDT", "BTC/USD", "BTCUSDT.P", "BTCUSD", "BTCUSDTP"},
    "stocks": {"TSLA", "HOOD", "CELH", "TTD", "PLTR", "AMZN", "NVDA", "AAPL", "META", "GOOGL", "MSFT", "SOFI"},
}

ASSET_META = {
    "xau":    {"label": "XAU/USD", "emoji": "🥇", "tv": "https://www.tradingview.com/chart/?symbol=OANDA:XAUUSD"},
    "dax":    {"label": "DAX",     "emoji": "🇩🇪", "tv": "https://www.tradingview.com/chart/?symbol=OANDA:DE30EUR"},
    "solana": {"label": "SOLANA",  "emoji": "💎", "tv": "https://www.tradingview.com/chart/?symbol=BITGET:SOLUSDT.P"},
    "btc":    {"label": "BITCOIN", "emoji": "₿",  "tv": "https://www.tradingview.com/chart/?symbol=BITGET:BTCUSDT.P"},
    "stocks": {"label": "STOCKS",  "emoji": "📈", "tv": "https://www.tradingview.com/chart/?symbol=NASDAQ:"},
}


def get_asset_group(asset: str) -> str:
    if not asset:
        return None
    a = asset.upper().replace("-", "").replace(".", "").replace("/", "")
    for group, assets in ASSET_GROUPS.items():
        for ref in assets:
            if a == ref.upper().replace("-", "").replace(".", "").replace("/", ""):
                return group
    return None


def get_tv_link(asset: str, group: str) -> str:
    if not group:
        return ""
    meta = ASSET_META.get(group, {})
    if group == "stocks" and asset:
        # sanitize : seul un ticker alphanumérique peut entrer dans l'URL
        safe = re.sub(r"[^A-Z0-9]", "", asset.upper())
        return f"https://www.tradingview.com/chart/?symbol=NASDAQ:{safe}"
    return meta.get("tv", "")


# Historiques en mémoire (alimentent le dashboard)
alert_history = deque(maxlen=200)
histories = {g: deque(maxlen=100) for g in ASSET_GROUPS}


# ── NEW v2.2.0 : rechargement de l'historique au démarrage ──
LEVEL_EMOJI = {"PRIORITAIRE": "🔴", "SECONDAIRE": "⚠️", "INFO": "📊"}


def load_alert_history(limit: int = 200):
    """Recharge les dernières alertes depuis SQLite au démarrage.
    Sans ça, le dashboard repart vide à chaque redéploiement même si la
    base persiste. La table alerts ne stocke pas emoji/details : on
    reconstruit l'emoji depuis 'level' et on laisse details vide."""
    try:
        with db() as conn:
            rows = conn.execute(
                "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        for r in reversed(rows):          # plus ancien → plus récent
            entry = {
                "id":        r["id"],
                "timestamp": r["ts"],
                "asset":     r["asset"],
                "timeframe": r["timeframe"],
                "type":      r["type"],
                "side":      r["side"],
                "price":     r["price"],
                "scope":     r["scope"],
                "score":     r["score"],
                "level":     r["level"],
                "emoji":     LEVEL_EMOJI.get(r["level"], "📊"),
                "details":   [],
            }
            alert_history.appendleft(entry)
            grp = r["grp"]
            if grp and grp in histories:
                histories[grp].appendleft(entry)
    except Exception as e:
        print(f"[DB] load_alert_history : {e}")


def clean_seed_rows():
    """Supprime les alertes de test (type 'SEED%') et leurs outcomes."""
    try:
        with db() as conn:
            ids = [r["id"] for r in conn.execute("SELECT id FROM alerts WHERE type LIKE 'SEED%'")]
            for aid in ids:
                conn.execute("DELETE FROM outcomes WHERE alert_id=?", (aid,))
                conn.execute("DELETE FROM alerts WHERE id=?", (aid,))
            conn.commit()
            if ids:
                print(f"[CLEAN] {len(ids)} ligne(s) SEED supprimée(s)")
    except Exception as e:
        print(f"[CLEAN] clean_seed_rows : {e}")


# ─────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────
def normalize_timeframe(tf: str) -> str:
    numeric_map = {
        "1": "M1", "2": "M2", "3": "M3", "4": "M4", "5": "M5", "10": "M10",
        "15": "M15", "30": "M30", "45": "M45",
        "60": "H1", "120": "H2", "180": "H3", "240": "H4",
        "360": "H6", "480": "H8", "720": "H12",
        "1440": "D1", "10080": "W1", "43200": "MN",
        # multi-journaliers en minutes (au cas où TradingView les envoie ainsi)
        "2880": "2D", "4320": "3D", "5760": "4D", "7200": "5D",
        # TF non-standard
        "72": "72m", "90": "90m", "96": "96m",
        "144": "144m", "160": "160m", "288": "288m",
    }
    return numeric_map.get(tf, tf)


def parse_fiblab_message(raw: str) -> dict:
    result = {
        "raw": raw.strip(), "type": None, "asset": None,
        "timeframe": None, "side": None, "price": None,
        "scope": None, "timestamp": now_iso(),
    }
    if "ATR PROXIMITY" in raw.upper():
        result["type"] = "ATR Proximity"
        m = re.search(r'TF:\s*([^\n\r|]+)', raw, re.IGNORECASE)
        if m:
            result["timeframe"] = normalize_timeframe(m.group(1).strip().upper())
        m = re.search(r'Side:\s*(Support|Resistance)', raw, re.IGNORECASE)
        if m:
            result["side"] = m.group(1).capitalize()
        m = re.search(r'Origin entry nearby:\s*([\d.]+)', raw, re.IGNORECASE)
        if m:
            result["price"] = float(m.group(1))
        result["scope"] = "Pure"
        return result

    if "—" in raw:
        parts = raw.split("—", 1)
        result["type"] = parts[0].strip()
        rest = parts[1].strip()
    else:
        rest = raw

    asset_tf = re.search(
        r'([A-Z0-9./]+)\s+([0-9]+[SMHDW]?|[HMDW][0-9]+|Daily|Weekly|Monthly)',
        rest, re.IGNORECASE
    )
    if asset_tf:
        result["asset"] = asset_tf.group(1).upper()
        result["timeframe"] = normalize_timeframe(asset_tf.group(2).upper())

    m = re.search(r'Side:\s*(Support|Resistance)', rest, re.IGNORECASE)
    if m:
        result["side"] = m.group(1).capitalize()
    m = re.search(r'Price:\s*([\d.]+)', rest)
    if m:
        result["price"] = float(m.group(1))
    m = re.search(r'Scope:\s*(Pure|Non-Pure)', rest, re.IGNORECASE)
    if m:
        result["scope"] = m.group(1)
    return result


# ─────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────
TF_WEIGHT = {
    "M1": 0, "M2": 0, "M3": 0, "M4": 0, "M5": 1, "M10": 1, "M15": 1, "M30": 1, "M45": 1,
    "H1": 2, "H2": 2, "H3": 2,
    "H4": 3, "H6": 3, "H8": 3, "H12": 3,
    "D1": 4, "1D": 4, "D": 4, "DAILY": 4,
    # ── FIX : les multi-journaliers, colonne vertébrale de la stratégie Origin ──
    "2D": 4, "3D": 5, "4D": 5, "5D": 5,
    "D2": 4, "D3": 5, "D4": 5, "D5": 5,
    "6D": 5, "7D": 5, "D6": 5, "D7": 5,   # NEW v2.2.0 : plus hauts TF enfin scorés
    "W1": 4, "1W": 4, "W": 4, "WEEKLY": 4, "MN": 4, "MONTHLY": 4,
    "72m": 1, "90m": 1, "96m": 1, "144m": 2, "160m": 2, "288m": 2,
}

TYPE_SCORES = {
    "origin untouched": 5, "origin first touch": 4,
    "broken origin first touch": 4, "broken first touch": 3,
    "break first touch": 3, "atr proximity": 3,
    "break created": 2, "origin broken": 2, "bsut created": 2,
    "origin touched": 1,
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

    if score >= 8:
        level, emoji = "PRIORITAIRE", "🔴"
    elif score >= 5:
        level, emoji = "SECONDAIRE", "⚠️"
    else:
        level, emoji = "INFO", "📊"

    return {"score": score, "level": level, "emoji": emoji, "details": details}


# ─────────────────────────────────────────────
# FILTRES — basés sur le profil utilisateur
# ─────────────────────────────────────────────
TF_SWING  = {"H4", "H6", "H8", "H12", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
             "W1", "MN", "1D", "2D", "3D", "4D", "5D", "6D", "7D", "1W", "4H", "8H", "12H"}
TF_SCALP  = {"M1", "M2", "M3", "M4", "M5", "M10", "M15", "M30", "M45", "H1", "H2", "H3", "H4", "4H"}
TF_CUSTOM = {"72m", "90m", "96m", "144m", "160m", "288m"}
TF_DAILY  = {"D1", "D2", "D3", "D4", "D5", "D6", "D7", "1D", "2D", "3D", "4D", "5D", "6D", "7D", "W1", "MN", "1W"}

TYPES_ALWAYS     = {"origin first touch", "origin untouched", "atr proximity",
                    "break first touch", "broken first touch", "broken origin first touch"}
TYPES_DAILY_ONLY = {"origin touched"}
TYPES_SCORE_MIN  = {"bsut created": 6}
TYPES_IGNORED    = {"break created"}


def should_notify(parsed: dict, scoring: dict, profile: dict) -> tuple:
    alert_type = (parsed.get("type") or "").lower()
    tf         = (parsed.get("timeframe") or "").upper()
    tf_lower   = tf.lower()
    mode       = profile["mode"]

    if tf_lower in TF_CUSTOM:
        key = tf_lower.replace("m", "")
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
            return False, "Type ignoré"

    for t, min_score in TYPES_SCORE_MIN.items():
        if t in alert_type:
            if scoring["score"] < min_score:
                return False, f"BSUT score {scoring['score']} < {min_score}"
            return True, "ok"

    for t in TYPES_DAILY_ONLY:
        if t in alert_type:
            if tf not in TF_DAILY:
                return False, "Origin Touched nécessite Daily+"
            return True, "ok"

    for t in TYPES_ALWAYS:
        if t in alert_type:
            return True, "ok"

    if scoring["score"] >= 5:
        return True, "ok"

    return False, "Score insuffisant"


# ─────────────────────────────────────────────
# TELEGRAM
# ─────────────────────────────────────────────
def send_telegram(message: str, chat_id: str = None, retries: int = 3):
    """Envoi Telegram avec retry + backoff (sans dépendance externe).
    429 / 5xx → on réessaie ; 4xx (hors 429) → abandon immédiat."""
    if not TELEGRAM_TOKEN:
        return False
    target = chat_id or TELEGRAM_CHAT_ID
    if not target:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": target, "text": message, "parse_mode": "HTML"}
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code == 200:
                return True
            if r.status_code != 429 and 400 <= r.status_code < 500:
                print(f"[TELEGRAM] HTTP {r.status_code} (non-retry) : {r.text[:120]}")
                return False
            print(f"[TELEGRAM] essai {attempt}/{retries} → HTTP {r.status_code}")
        except requests.RequestException as e:
            print(f"[TELEGRAM] essai {attempt}/{retries} → {e}")
        if attempt < retries:
            time.sleep(min(2 ** (attempt - 1), 4))   # 1s, 2s, (cap 4s)
    print(f"[TELEGRAM] échec après {retries} essais pour {target}")
    return False


def format_telegram_message(parsed: dict, scoring: dict, profile: dict = None) -> str:
    asset   = parsed.get("asset") or None
    group   = get_asset_group(asset) if asset else None
    meta    = ASSET_META.get(group, {"emoji": "📡", "label": asset or "?"})
    is_atr  = "atr" in (parsed.get("type") or "").lower()
    tv_link = get_tv_link(asset, group)
    mode    = (profile or {}).get("mode", "swing")

    side_emoji    = "🟢" if parsed.get("side") == "Support" else "🔴"
    scope_tag     = "✅ Pure" if parsed.get("scope") == "Pure" else "⬜ Non-Pure"
    asset_display = f"{meta['emoji']} {esc(asset)}" if asset else f"{meta['emoji']} voir chart"
    action = (
        "→ Surveille M1 maintenant\n→ Setup <b>LONG</b> potentiel\n→ SL visé : 5-10 pts"
        if parsed.get("side") == "Support" else
        "→ Surveille M1 maintenant\n→ Setup <b>SHORT</b> potentiel\n→ SL visé : 5-10 pts"
    )

    msg = (
        f"{scoring['emoji']} <b>ALERTE {scoring['level']} — Score {scoring['score']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Asset    : <b>{asset_display}</b>\n"
        f"Niveau   : <b>{esc(parsed.get('price', '?'))}</b>\n"
        f"Type     : {'📡 ' if is_atr else ''}{esc(parsed.get('type', '?'))}\n"
        f"TF       : {esc(parsed.get('timeframe', '?'))}\n"
        f"Side     : {side_emoji} {esc(parsed.get('side', '?'))}\n"
        f"Scope    : {scope_tag}\n"
        f"Mode     : {esc(mode.upper())}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Scoring :\n"
    )
    for d in scoring["details"]:
        msg += f"  • {esc(d)}\n"

    tv_line = f"\n📈 <a href='{esc(tv_link)}'>Ouvrir le chart</a>" if tv_link else ""
    msg += (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Action :\n{action}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {esc(parsed.get('timestamp', '')[:19].replace('T', ' '))} UTC"
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
        if arg in ("swing", "scalp", "both"):
            profile["mode"] = arg
            labels = {"swing": "🔵 SWING (H4+)", "scalp": "⚡ SCALP (M1→H4)", "both": "🌐 BOTH (tout)"}
            msg = f"✅ Ton mode → <b>{labels[arg]}</b>\n(ne change rien pour les autres utilisateurs)"
        else:
            msg = "Usage : /mode swing | /mode scalp | /mode both"

    elif cmd == "/tf_on":
        if arg in profile["tf_custom"]:
            profile["tf_custom"][arg] = True
            msg = f"✅ TF <b>{esc(arg)}m</b> activé pour toi"
        else:
            msg = f"TF '{esc(arg)}' inconnu. Disponibles : 72 90 96 144 160 288"

    elif cmd == "/tf_off":
        if arg in profile["tf_custom"]:
            profile["tf_custom"][arg] = False
            msg = f"⛔ TF <b>{esc(arg)}m</b> désactivé pour toi"
        else:
            msg = f"TF '{esc(arg)}' inconnu. Disponibles : 72 90 96 144 160 288"

    elif cmd == "/tf_status":
        actifs   = [k for k, v in profile["tf_custom"].items() if v]
        inactifs = [k for k, v in profile["tf_custom"].items() if not v]
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

    elif cmd == "/killswitch":
        # Commande admin : coupe/réactive TOUTES les notifications, tous utilisateurs
        if chat_id != TELEGRAM_CHAT_ID:
            msg = "⛔ Commande réservée à l'admin."
        elif arg == "on":
            robot_state["paused"] = True
            msg = "🛑 <b>KILLSWITCH ON</b> — toutes notifications coupées (tous utilisateurs)."
        elif arg == "off":
            robot_state["paused"] = False
            msg = "✅ <b>KILLSWITCH OFF</b> — notifications réactivées."
        else:
            etat = "ON 🛑" if robot_state["paused"] else "OFF ✅"
            msg = f"Killswitch actuel : <b>{etat}</b>\nUsage : /killswitch on | /killswitch off"

    elif cmd == "/status":
        tf_on = [k for k, v in profile["tf_custom"].items() if v]
        etat  = "⏸ PAUSE" if profile["paused"] else "✅ ACTIF"
        kill  = "🛑 KILLSWITCH ON" if robot_state["paused"] else ""
        msg = (
            f"🤖 <b>Ton profil FibLab Robot</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"État   : {etat} {kill}\n"
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

    elif cmd in ("/derniere", "/xau", "/solana", "/dax", "/btc", "/stocks"):
        key    = cmd[1:] if cmd[1:] in histories else None
        hist   = histories[key] if key else alert_history
        labels = {"xau": "🥇 XAU", "solana": "💎 Solana", "dax": "🇩🇪 DAX", "btc": "₿ BTC", "stocks": "📈 Stocks"}
        prefix = labels.get(key, "📊 Toutes")
        if hist:
            a  = hist[0]
            sc = {"score": a.get("score", 0), "level": a.get("level", ""),
                  "emoji": a.get("emoji", ""), "details": a.get("details", [])}
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

    # Persistance du profil après toute commande (upsert idempotent)
    try:
        save_profile(chat_id, profile)
    except Exception as e:
        print(f"[DB] save_profile : {e}")

    send_telegram(msg, chat_id)


# ─────────────────────────────────────────────
# ÉVALUATION AUTOMATIQUE DES ISSUES (v2.3.0)
# ─────────────────────────────────────────────
# Mesure, pour chaque alerte 'pending' assez ancienne, si le NIVEAU a produit
# un mouvement favorable. C'est un PROXY DIRECTIONNEL pour calibrer le scoring
# (un score 12 réagit-il mieux qu'un score 7 ?), PAS le P&L exact de ton trade
# qui dépend de ton englobante/SL réel.
#
# Source : Twelve Data si TWELVEDATA_API_KEY défini (couverture homogène),
# sinon Yahoo keyless (XAU via le futur GC=F → léger basis vs ton feed Vantage).
# Granularité H1.

TWELVEDATA_API_KEY = os.environ.get("TWELVEDATA_API_KEY", "")

EVAL_MIN_AGE_H      = 12      # age minimum d'une alerte avant 1re evaluation (h)
EVAL_ATR_BARS       = 14      # nb de bougies (au TF de l'alerte) pour l'ATR
EVAL_HORIZON_BARS   = 12      # fenetre d'observation = 12 bougies du TF de l'alerte
EVAL_HORIZON_MIN_H  = 48      # plancher de la fenetre (h)
EVAL_HORIZON_MAX_H  = 504     # plafond de la fenetre = 21 jours (h)
EVAL_LOOKBACK_MAX_H = 504     # plafond du lookback ATR (h)

# Stop ADAPTATIF par timeframe : SL = k * ATR(au TF de l'alerte), borne par
# [sl_floor, sl_cap]. fallback = SL fixe si l'ATR ne peut pas etre calcule.
# tp_r = multiple de R vise (TP = tp_r * SL).
EVAL_RISK = {
    "xau":    {"k": 1.0, "tp_r": 3.0, "sl_floor": 3.0,  "sl_cap": 150.0,  "fallback": 15.0},
    "dax":    {"k": 1.0, "tp_r": 3.0, "sl_floor": 8.0,  "sl_cap": 400.0,  "fallback": 30.0},
    "btc":    {"k": 1.0, "tp_r": 3.0, "sl_floor": 80.0, "sl_cap": 6000.0, "fallback": 400.0},
    "solana": {"k": 1.0, "tp_r": 3.0, "sl_floor": 0.5,  "sl_cap": 40.0,   "fallback": 2.0},
    "stocks": {"k": 1.0, "tp_r": 3.0, "sl_floor": 0.3,  "sl_cap": 60.0,   "fallback": 2.0},
}

# Duree (heures) d'une bougie par timeframe -> dimensionne ATR, lookback et horizon
TF_HOURS = {
    "M1": 1, "M2": 1, "M3": 1, "M4": 1, "M5": 1, "M10": 1, "M15": 1, "M30": 1, "M45": 1,
    "H1": 1, "H2": 2, "H3": 3, "H4": 4, "H6": 6, "H8": 8, "H12": 12,
    "D1": 24, "1D": 24, "D": 24, "DAILY": 24,
    "2D": 48, "3D": 72, "4D": 96, "5D": 120, "6D": 144, "7D": 168,
    "D2": 48, "D3": 72, "D4": 96, "D5": 120, "D6": 144, "D7": 168,
    "W1": 168, "1W": 168, "W": 168, "WEEKLY": 168, "MN": 336, "MONTHLY": 336,
    "72m": 1, "90m": 2, "96m": 2, "144m": 2, "160m": 3, "288m": 5,
}


def tf_hours(tf):
    if not tf:
        return 4
    return TF_HOURS.get(tf, TF_HOURS.get(tf.upper(), 4))


def _atr_at_tf(pre_bars, tf_h):
    """ATR (base sur le range haut-bas) au timeframe de l'alerte, calcule a partir
    de bougies H1 anterieures a l'alerte, regroupees en paquets de la taille du TF."""
    if len(pre_bars) < 2:
        return None
    bucket = max(1, int(round(tf_h)))
    ranges = []
    i = 0
    while i + bucket <= len(pre_bars):
        chunk = pre_bars[i:i + bucket]
        ranges.append(max(b[1] for b in chunk) - min(b[2] for b in chunk))
        i += bucket
    if not ranges:
        return None
    last = ranges[-EVAL_ATR_BARS:]
    return sum(last) / len(last)

SYMBOL_MAP_YF = {"xau": "GC=F", "dax": "^GDAXI", "btc": "BTC-USD", "solana": "SOL-USD"}
SYMBOL_MAP_TD = {"xau": "XAU/USD", "dax": "DAX", "btc": "BTC/USD", "solana": "SOL/USD"}


def _yahoo_symbol(group, asset):
    if group == "stocks":
        return re.sub(r"[^A-Z0-9.\-]", "", (asset or "").upper())
    return SYMBOL_MAP_YF.get(group)


def _twelvedata_symbol(group, asset):
    if group == "stocks":
        return re.sub(r"[^A-Z0-9.\-]", "", (asset or "").upper())
    return SYMBOL_MAP_TD.get(group)


def _fetch_yahoo(symbol, start_dt, end_dt):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"period1": int(start_dt.timestamp()),
              "period2": int(end_dt.timestamp()), "interval": "1h"}
    r = requests.get(url, params=params, timeout=8,
                     headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    res = (r.json().get("chart", {}).get("result") or [None])[0]
    if not res:
        return []
    ts = res.get("timestamp") or []
    q = (res.get("indicators", {}).get("quote") or [{}])[0]
    highs, lows = q.get("high") or [], q.get("low") or []
    bars = []
    for i, t in enumerate(ts):
        hi = highs[i] if i < len(highs) else None
        lo = lows[i] if i < len(lows) else None
        if hi is not None and lo is not None:
            bars.append((datetime.fromtimestamp(t, tz=timezone.utc), float(hi), float(lo)))
    return bars


def _fetch_twelvedata(symbol, start_dt, end_dt):
    url = "https://api.twelvedata.com/time_series"
    params = {"symbol": symbol, "interval": "1h",
              "start_date": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
              "end_date": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
              "apikey": TWELVEDATA_API_KEY, "timezone": "UTC", "outputsize": 5000}
    r = requests.get(url, params=params, timeout=8)
    r.raise_for_status()
    vals = r.json().get("values")
    if not vals:
        return []
    bars = []
    for v in vals:
        try:
            dt = datetime.strptime(v["datetime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            bars.append((dt, float(v["high"]), float(v["low"])))
        except Exception:
            continue
    bars.sort(key=lambda x: x[0])
    return bars


def fetch_prices(group, asset, start_dt, end_dt):
    """[(datetime, high, low), ...] en H1. Twelve Data si clé, sinon Yahoo."""
    try:
        if TWELVEDATA_API_KEY:
            sym = _twelvedata_symbol(group, asset)
            if sym:
                return _fetch_twelvedata(sym, start_dt, end_dt)
        sym = _yahoo_symbol(group, asset)
        if sym:
            return _fetch_yahoo(sym, start_dt, end_dt)
    except Exception as e:
        print(f"[EVAL] fetch_prices {group}/{asset} : {e}")
    return []


def evaluate_pending_outcomes():
    """Evalue les alertes 'pending' assez anciennes, avec un STOP ADAPTATIF au
    timeframe (SL = k*ATR du TF) et une FENETRE proportionnelle au TF. Un niveau
    Daily est donc juge avec un stop large et plus de temps qu'un H4.
    Regle : depuis le niveau, dans le sens du Side, win si +tp_r*SL atteint avant
    -SL ; loss sinon ; 'invalid' seulement si la fenetre est entierement ecoulee
    (sinon l'alerte reste 'pending' et sera reevaluee plus tard). Intrabar : SL
    teste avant TP (conservateur). Proxy directionnel, pas le P&L reel du trade."""
    now = datetime.now(timezone.utc)
    with db() as conn:
        rows = conn.execute(
            "SELECT a.id, a.ts, a.asset, a.grp, a.side, a.price, a.timeframe "
            "FROM alerts a JOIN outcomes o ON a.id = o.alert_id "
            "WHERE o.status = 'pending' AND a.price IS NOT NULL AND a.side IS NOT NULL "
            "ORDER BY a.id LIMIT 100"
        ).fetchall()

    evaluated = 0
    _start = time.monotonic()
    for r in rows:
        if time.monotonic() - _start > 20:        # budget temps : finir avant le timeout du cron
            break
        try:
            ts = datetime.fromisoformat(r["ts"])
        except Exception:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if (now - ts).total_seconds() / 3600 < EVAL_MIN_AGE_H:
            continue
        risk = EVAL_RISK.get(r["grp"])
        if not risk:
            continue

        tf_h       = tf_hours(r["timeframe"])
        horizon_h  = min(max(EVAL_HORIZON_BARS * tf_h, EVAL_HORIZON_MIN_H), EVAL_HORIZON_MAX_H)
        lookback_h = min(EVAL_ATR_BARS * tf_h, EVAL_LOOKBACK_MAX_H)
        end_dt     = min(ts + timedelta(hours=horizon_h), now)
        start_dt   = ts - timedelta(hours=lookback_h)

        bars = fetch_prices(r["grp"], r["asset"], start_dt, end_dt)
        if not bars:
            continue
        pre  = [b for b in bars if b[0] <= ts]
        post = [b for b in bars if b[0] > ts]
        if not post:
            continue

        atr = _atr_at_tf(pre, tf_h)
        if atr and atr > 0:
            sl, sl_src = min(max(risk["k"] * atr, risk["sl_floor"]), risk["sl_cap"]), "atr"
        else:
            sl, sl_src = risk["fallback"], "fallback"
        tp = sl * risk["tp_r"]
        entry = r["price"]
        long_bias = (r["side"] == "Support")

        mfe = mae = 0.0
        status = None
        r_real = None
        for (_dt, hi, lo) in post:
            fav = (hi - entry) if long_bias else (entry - lo)
            adv = (entry - lo) if long_bias else (hi - entry)
            mfe = max(mfe, fav)
            mae = max(mae, adv)
            if adv >= sl:
                status, r_real = "loss", -1.0
                break
            if fav >= tp:
                status, r_real = "win", risk["tp_r"]
                break

        if status is None:
            if now >= ts + timedelta(hours=horizon_h):
                status, r_real = "invalid", (round(mfe / sl, 2) if sl else None)
            else:
                continue          # fenetre pas encore ecoulee -> reste 'pending'

        src = "twelvedata" if TWELVEDATA_API_KEY else "yahoo"
        note = (f"auto ({src}, TF={r['timeframe']}, SL={round(sl, 2)}[{sl_src}], "
                f"TP={round(tp, 2)}, H={int(horizon_h)}h)")
        with db() as conn:
            conn.execute(
                "UPDATE outcomes SET status=?, mfe_pts=?, mae_pts=?, r_realized=?, "
                "note=?, updated_ts=? WHERE alert_id=?",
                (status, round(mfe, 2), round(mae, 2), r_real, note, now_iso(), r["id"])
            )
            conn.commit()
        evaluated += 1
    return evaluated


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403

    raw = request.get_data(as_text=True).strip()
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            raw  = data.get("message", data.get("text", raw))
        except Exception:
            pass

    print(f"[WEBHOOK] Reçu : {raw[:100]}")
    if not raw:
        return jsonify({"error": "empty body"}), 400

    parsed  = parse_fiblab_message(raw)
    scoring = compute_score(parsed)
    group   = get_asset_group(parsed.get("asset") or "")

    # Persistance + id pour le suivi d'issue
    try:
        alert_id = save_alert(parsed, scoring, group)
    except Exception as e:
        print(f"[DB] save_alert : {e}")
        alert_id = None

    entry = {**parsed, **scoring, "id": alert_id}
    alert_history.appendleft(entry)
    if group and group in histories:
        histories[group].appendleft(entry)

    if robot_state["paused"]:
        return jsonify({"status": "killswitch", "id": alert_id}), 200

    results = {}
    for user_id in [TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_2]:
        if not user_id:
            continue
        profile = get_profile(user_id)
        if profile["paused"]:
            continue
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

    print(f"[WEBHOOK] {scoring['level']} Score={scoring['score']} "
          f"TF={parsed.get('timeframe')} Group={group} id={alert_id} {results}")
    return jsonify({"status": "ok", "id": alert_id, "scoring": scoring,
                    "group": group, "results": results}), 200


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


@app.route("/outcome/<int:alert_id>", methods=["POST"])
def set_outcome(alert_id):
    """Tague manuellement l'issue d'une alerte (en attendant l'auto-éval)."""
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    d = request.get_json(silent=True) or {}
    status = d.get("status")
    if status not in ("pending", "win", "loss", "invalid"):
        return jsonify({"error": "status invalide (pending|win|loss|invalid)"}), 400
    with db() as conn:
        conn.execute(
            "UPDATE outcomes SET status=?, mfe_pts=?, mae_pts=?, r_realized=?, note=?, updated_ts=? "
            "WHERE alert_id=?",
            (status, d.get("mfe_pts"), d.get("mae_pts"), d.get("r_realized"),
             d.get("note"), now_iso(), alert_id)
        )
        conn.commit()
    return jsonify({"updated": alert_id, "status": status})


@app.route("/stats", methods=["GET"])
def stats():
    """Win rate par score et par type — le coeur de la calibration future."""
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    with db() as conn:
        rows = conn.execute(
            "SELECT a.score, a.type, a.timeframe, o.status "
            "FROM alerts a JOIN outcomes o ON a.id = o.alert_id"
        ).fetchall()

    by_score, by_type, by_tf = {}, {}, {}
    for r in rows:
        if r["status"] not in ("win", "loss"):
            continue
        by_score.setdefault(r["score"], {"win": 0, "loss": 0})[r["status"]] += 1
        by_type.setdefault(r["type"] or "?", {"win": 0, "loss": 0})[r["status"]] += 1
        by_tf.setdefault(r["timeframe"] or "?", {"win": 0, "loss": 0})[r["status"]] += 1

    def wr(d):
        tot = d["win"] + d["loss"]
        return round(100 * d["win"] / tot, 1) if tot else None

    def enrich(bucket):
        return {str(k): {**v, "win_rate_%": wr(v)} for k, v in sorted(bucket.items(), key=lambda x: str(x[0]))}

    return jsonify({
        "evaluated": sum(v["win"] + v["loss"] for v in by_score.values()),
        "by_score": enrich(by_score),
        "by_type":  enrich(by_type),
        "by_tf":    enrich(by_tf),
    })


@app.route("/evaluate", methods=["GET", "POST"])
def evaluate_route():
    """Lance l'évaluation des issues 'pending'. À pinger périodiquement
    (cron-job.org, Railway cron...) ou à la main. Renvoie le nb traité."""
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    n = evaluate_pending_outcomes()
    with db() as conn:
        remaining = conn.execute("SELECT COUNT(*) AS n FROM outcomes WHERE status='pending'").fetchone()["n"]
    return jsonify({"evaluated": n, "remaining_pending": remaining})


@app.route("/reeval", methods=["GET", "POST"])
def reeval_route():
    """Remet TOUTES les issues a 'pending' pour reevaluation avec la methode
    adaptative en cours. A lancer une fois apres un changement de methode."""
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    with db() as conn:
        cur = conn.execute(
            "UPDATE outcomes SET status='pending', mfe_pts=NULL, mae_pts=NULL, "
            "r_realized=NULL, note=NULL WHERE status != 'pending'"
        )
        conn.commit()
        n = cur.rowcount
    return jsonify({"reset_to_pending": n})


@app.route("/price_test", methods=["GET"])
def price_test():
    """Vérifie que la source de prix répond (utile si Yahoo bloque l'IP Railway)."""
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=48)
    bars = fetch_prices("xau", "XAUUSD", start, end)
    src = "twelvedata" if TWELVEDATA_API_KEY else "yahoo"
    sample = [{"t": b[0].isoformat(), "high": b[1], "low": b[2]} for b in bars[:3]]
    return jsonify({"source": src, "bars": len(bars), "sample": sample})


# ─────────────────────────────────────────────
# TABLEAU DE BORD DE CALIBRATION (v2.4.1 — rendu serveur, sans JS ni CDN)
# ─────────────────────────────────────────────
DASH_CSS = """<style>
:root{--bg:#080c10;--card:#0d1117;--bd:#1c2333;--gold:#f5a623;--grn:#3fb950;--red:#f85149;--blue:#58a6ff;--pur:#a78bfa;--tx:#cdd9e5;--dim:#768390}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--tx);font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;padding:20px;max-width:1000px;margin:0 auto}
h1{font-size:1.5rem;color:var(--gold);margin-bottom:4px}
.sub{color:var(--dim);font-size:.8rem;margin-bottom:20px}
.refresh{float:right;font-size:.75rem;color:var(--blue);text-decoration:none;border:1px solid var(--bd);padding:5px 10px;border-radius:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:22px}
.stat{background:var(--card);border:1px solid var(--bd);border-radius:8px;padding:13px}
.lbl{font-size:.6rem;text-transform:uppercase;letter-spacing:.08em;color:var(--dim);margin-bottom:5px}
.val{font-size:1.5rem;font-weight:700}
.card{background:var(--card);border:1px solid var(--bd);border-radius:8px;padding:16px;margin-bottom:18px}
.card h2{font-size:.9rem;margin-bottom:14px;color:var(--blue)}
.brow{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:.8rem}
.blab{width:54px;text-align:right;color:var(--tx);flex-shrink:0}
.btrack{flex:1;height:20px;background:#0a0e14;border:1px solid var(--bd);border-radius:5px;overflow:hidden}
.bfill{height:100%;border-radius:4px 0 0 4px;min-width:2px}
.bval{width:172px;text-align:left;flex-shrink:0}
.bn{color:var(--dim);font-size:.72rem}
.note{background:rgba(88,166,255,.06);border:1px solid rgba(88,166,255,.2);border-radius:8px;padding:14px;font-size:.8rem;line-height:1.6;margin-bottom:18px}
table{width:100%;border-collapse:collapse;font-size:.8rem}
th{text-align:left;padding:7px 9px;font-size:.6rem;text-transform:uppercase;color:var(--dim);border-bottom:1px solid var(--bd)}
td{padding:7px 9px;border-bottom:1px solid var(--bd)}
.empty{text-align:center;color:var(--dim);padding:40px;font-size:.9rem;line-height:1.7}
.muted{color:var(--dim);font-size:.8rem;padding:8px}
code{background:#161b22;padding:2px 6px;border-radius:4px;color:var(--gold)}
</style>"""


def _bar_rows(rows, color):
    if not rows:
        return '<div class="muted">aucune donn\u00e9e</div>'
    out = []
    for r in rows:
        fill = color + ("55" if r["n"] < 5 else "")
        wrc = "var(--grn)" if r["wr"] >= 50 else "var(--gold)"
        out.append(
            '<div class="brow">'
            + '<div class="blab">' + esc(r["k"]) + '</div>'
            + '<div class="btrack"><div class="bfill" style="width:' + str(r["wr"]) + '%;background:' + fill + '"></div></div>'
            + '<div class="bval" style="color:' + wrc + '">' + str(r["wr"]) + '% '
            + '<span class="bn">(' + str(r["win"]) + 'W/' + str(r["loss"]) + 'L \u00b7 n=' + str(r["n"]) + ')</span></div>'
            + '</div>')
    return "".join(out)


@app.route("/stats_view", methods=["GET"])
def stats_view():
    """Tableau de bord de calibration — rendu 100% serveur (aucune dependance externe)."""
    if not check_secret():
        return ("unauthorized", 403)
    with db() as conn:
        rows = conn.execute(
            "SELECT a.score, a.type, a.timeframe, o.status "
            "FROM alerts a JOIN outcomes o ON a.id = o.alert_id"
        ).fetchall()

    counts = {"win": 0, "loss": 0, "invalid": 0, "pending": 0, "skip": 0}
    by_score, by_type, by_tf = {}, {}, {}
    for r in rows:
        st = r["status"] or "pending"
        counts[st] = counts.get(st, 0) + 1
        if st in ("win", "loss"):
            by_score.setdefault(r["score"], {"win": 0, "loss": 0})[st] += 1
            by_type.setdefault(r["type"] or "?", {"win": 0, "loss": 0})[st] += 1
            by_tf.setdefault(r["timeframe"] or "?", {"win": 0, "loss": 0})[st] += 1

    def pack(b, numeric=False):
        items = []
        for k, v in b.items():
            tot = v["win"] + v["loss"]
            items.append({"k": str(k), "_s": k, "win": v["win"], "loss": v["loss"],
                          "n": tot, "wr": round(100 * v["win"] / tot, 1) if tot else 0})
        items.sort(key=lambda x: x["_s"] if numeric else str(x["_s"]))
        for it in items:
            del it["_s"]
        return items

    bs, bt, btf = pack(by_score, True), pack(by_type), pack(by_tf)
    tot_eval = counts["win"] + counts["loss"]
    wr = round(100 * counts["win"] / tot_eval, 1) if tot_eval else 0

    head = ('<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>FibLab \u2014 Calibration</title>' + DASH_CSS + '</head><body>')
    header = ('<a class="refresh" href="/stats_view">\u21bb Rafra\u00eechir</a>'
              '<h1>\U0001F3AF Calibration du scoring</h1>'
              '<div class="sub">Win rate des alertes par score / type / timeframe '
              '\u2014 pour ajuster les poids sur des faits</div>')

    if tot_eval == 0:
        body = ('<div class="empty">Aucune alerte \u00e9valu\u00e9e pour l\'instant.<br><br>'
                'Les alertes sont not\u00e9es automatiquement une fois pass\u00e9es 12h ('
                + str(counts["pending"]) + ' en attente).<br>'
                'V\u00e9rifie aussi que le cron <code>/evaluate</code> tourne sans erreur.</div>')
        return head + header + body + '</body></html>'

    wrc = "var(--grn)" if wr >= 50 else "var(--gold)"
    cards = ('<div class="grid">'
             '<div class="stat"><div class="lbl">\u00c9valu\u00e9es</div><div class="val" style="color:var(--blue)">' + str(tot_eval) + '</div></div>'
             '<div class="stat"><div class="lbl">Win rate global</div><div class="val" style="color:' + wrc + '">' + str(wr) + '%</div></div>'
             '<div class="stat"><div class="lbl">Win</div><div class="val" style="color:var(--grn)">' + str(counts["win"]) + '</div></div>'
             '<div class="stat"><div class="lbl">Loss</div><div class="val" style="color:var(--red)">' + str(counts["loss"]) + '</div></div>'
             '<div class="stat"><div class="lbl">Invalid</div><div class="val" style="color:var(--dim)">' + str(counts["invalid"]) + '</div></div>'
             '<div class="stat"><div class="lbl">En attente</div><div class="val" style="color:var(--dim)">' + str(counts["pending"]) + '</div></div>'
             '</div>')
    note = ('<div class="note"><b>Comment lire :</b> si ton scoring est bon, le win rate doit '
            '<b>monter avec le score</b> (un 12 gagne plus qu\'un 7). Si une barre de score faible '
            'd\u00e9passe celle d\'un score fort, les <b>poids sont \u00e0 recalibrer</b>. '
            'Barres p\u00e2les = moins de 5 trades (peu fiable).</div>')
    trows = []
    for r in bs:
        c = "var(--grn)" if r["wr"] >= 50 else "var(--gold)"
        trows.append('<tr><td>' + esc(r["k"]) + '</td><td style="color:var(--grn)">' + str(r["win"])
                     + '</td><td style="color:var(--red)">' + str(r["loss"]) + '</td><td>' + str(r["n"])
                     + '</td><td style="font-weight:700;color:' + c + '">' + str(r["wr"]) + '%</td></tr>')
    table = ('<div class="card"><h2>D\u00e9tail par score</h2><table><thead><tr>'
             '<th>Score</th><th>Win</th><th>Loss</th><th>N</th><th>Win rate</th></tr></thead><tbody>'
             + "".join(trows) + '</tbody></table></div>')

    body = (cards
            + '<div class="card"><h2>Win rate par SCORE \u2014 le graphe cl\u00e9</h2>' + _bar_rows(bs, "#f5a623") + '</div>'
            + note
            + '<div class="card"><h2>Win rate par TYPE</h2>' + _bar_rows(bt, "#58a6ff") + '</div>'
            + '<div class="card"><h2>Win rate par TIMEFRAME</h2>' + _bar_rows(btf, "#a78bfa") + '</div>'
            + table)
    return head + header + body + '</body></html>'


@app.route("/db_count", methods=["GET"])
def db_count():
    """NEW v2.2.0 — compte réel en base, pour prouver que le volume persiste.
    Test : appeler /test deux-trois fois → redéployer → si ce compteur ne
    repart pas à zéro, la persistance fonctionne."""
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    with db() as conn:
        a = conn.execute("SELECT COUNT(*) AS n FROM alerts").fetchone()["n"]
        o = conn.execute("SELECT COUNT(*) AS n FROM outcomes").fetchone()["n"]
        p = conn.execute("SELECT COUNT(*) AS n FROM profiles").fetchone()["n"]
    return jsonify({"alerts": a, "outcomes": o, "profiles": p, "db_path": DB_PATH})


@app.route("/status", methods=["GET"])
def status():
    profiles_summary = {uid: {"mode": p["mode"], "paused": p["paused"]}
                        for uid, p in user_profiles.items()}
    return jsonify({
        "status": "killswitch" if robot_state["paused"] else "running",
        "alerts_total": len(alert_history),
        **{f"alerts_{g}": len(h) for g, h in histories.items()},
        "user_profiles": profiles_summary,
    })


@app.route("/", methods=["GET"])
def dashboard_all():
    return render_template("dashboard.html", alerts=list(alert_history), page="all",
                           counts={g: len(h) for g, h in histories.items()})


@app.route("/xau", methods=["GET"])
def dashboard_xau():
    return render_template("dashboard.html", alerts=list(histories["xau"]), page="xau",
                           counts={g: len(h) for g, h in histories.items()})


@app.route("/solana", methods=["GET"])
def dashboard_solana():
    return render_template("dashboard.html", alerts=list(histories["solana"]), page="solana",
                           counts={g: len(h) for g, h in histories.items()})


@app.route("/dax", methods=["GET"])
def dashboard_dax():
    return render_template("dashboard.html", alerts=list(histories["dax"]), page="dax",
                           counts={g: len(h) for g, h in histories.items()})


@app.route("/btc", methods=["GET"])
def dashboard_btc():
    return render_template("dashboard.html", alerts=list(histories["btc"]), page="btc",
                           counts={g: len(h) for g, h in histories.items()})


@app.route("/stocks", methods=["GET"])
def dashboard_stocks():
    return render_template("dashboard.html", alerts=list(histories["stocks"]), page="stocks",
                           counts={g: len(h) for g, h in histories.items()})


@app.route("/levels", methods=["GET"])
def levels():
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(list(alert_history))


def _test(fake: str):
    parsed  = parse_fiblab_message(fake)
    scoring = compute_score(parsed)
    group   = get_asset_group(parsed.get("asset") or "")
    try:
        save_alert(parsed, scoring, group)
    except Exception as e:
        print(f"[DB] _test save_alert : {e}")
    msg = format_telegram_message(parsed, scoring, get_profile(TELEGRAM_CHAT_ID))
    sent_charlie = send_telegram(msg, TELEGRAM_CHAT_ID)
    sent_frere   = send_telegram(msg, TELEGRAM_CHAT_ID_2) if TELEGRAM_CHAT_ID_2 else False
    return jsonify({"telegram_charlie": sent_charlie, "telegram_frere": sent_frere,
                    "frere_configured": bool(TELEGRAM_CHAT_ID_2), "scoring": scoring})


@app.route("/test", methods=["GET"])
def test_xau():
    return _test("Origin Untouched — XAUUSD 2D | Side: Support | Price: 4310.00 | Scope: Pure")


@app.route("/test_solana", methods=["GET"])
def test_solana():
    return _test("Origin First Touch — SOLUSDT.P H4 | Side: Support | Price: 142.50 | Scope: Pure")


@app.route("/test_dax", methods=["GET"])
def test_dax():
    return _test("Broken First Touch — DE30EUR H4 | Side: Resistance | Price: 24850.00 | Scope: Pure")


@app.route("/test_btc", methods=["GET"])
def test_btc():
    return _test("Origin First Touch — BTCUSDT.P H4 | Side: Support | Price: 98500.00 | Scope: Pure")


@app.route("/test_stocks", methods=["GET"])
def test_stocks():
    return _test("Origin First Touch — TSLA H4 | Side: Support | Price: 285.00 | Scope: Pure")


# ─────────────────────────────────────────────
# INIT (au chargement du module → fonctionne aussi sous gunicorn)
# ─────────────────────────────────────────────
init_db()
clean_seed_rows()                # v2.4.0 : retire les lignes de test SEED
load_profiles()
load_alert_history()             # restaure le dashboard après redéploiement


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
