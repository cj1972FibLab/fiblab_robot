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
# CONFIGURATION — À remplir dans Railway (env vars)
# ─────────────────────────────────────────────
TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
SECRET_KEY      = os.environ.get("WEBHOOK_SECRET", "")   # optionnel

# Historique en mémoire (50 dernières alertes)
alert_history = deque(maxlen=50)

# ─────────────────────────────────────────────
# PARSER — Fib Lab message → dict structuré
# ─────────────────────────────────────────────
def normalize_timeframe(tf: str) -> str:
    """
    Convertit les timeframes numériques TradingView en labels lisibles.
    TradingView envoie des minutes brutes : 60 = H1, 240 = H4, 1440 = D1, etc.
    """
    numeric_map = {
        "1":    "M1",
        "3":    "M3",
        "5":    "M5",
        "10":   "M10",
        "15":   "M15",
        "30":   "M30",
        "45":   "M45",
        "60":   "H1",
        "120":  "H2",
        "180":  "H3",
        "240":  "H4",
        "360":  "H6",
        "480":  "H8",
        "720":  "H12",
        "1440": "D1",
        "10080":"W1",
        "43200":"MN",
    }
    return numeric_map.get(tf, tf)


def parse_fiblab_message(raw: str) -> dict:
    """
    Exemples gérés :
      Origin First Touch — XAUUSD 30S | Side: Support | Price: 4463.00 | Scope: Non-Pure
      Broken First Touch — XAUUSD 30S | Side: Support | Price: 4464.58 | Scope: Pure
      Break Created — XAUUSD 30S | Side: Resistance | Price: 4465.87 | Scope: Non-Pure
      Break First Touch — XAUUSD 30S | Side: Resistance | Price: 4465.87 | Scope: Non-Pure
      Origin Broken: Origin BSUT Created — XAUUSD 30S | Side: Resistance | Price: 4465.81 | Scope: Non-Pure
      Broken Origin First Touch — XAUUSD 30S | Side: Support | Price: 4465.81 | Scope: Non-Pure
    """
    result = {
        "raw": raw.strip(),
        "type": None,
        "asset": None,
        "timeframe": None,
        "side": None,
        "price": None,
        "scope": None,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Séparation type / reste sur "—"
    if "—" in raw:
        parts = raw.split("—", 1)
        result["type"] = parts[0].strip()
        rest = parts[1].strip()
    else:
        # Format "Origin Broken: Origin BSUT Created — ..."
        rest = raw

    # Asset + Timeframe
    # Gère : XAUUSD 30S, BTCUSDT H4, XAUUSD 60, XAUUSD 1440, etc.
    asset_tf = re.search(r'([A-Z0-9./]+)\s+([0-9]+[SMHD]?|Daily|Weekly|Monthly)', rest, re.IGNORECASE)
    if asset_tf:
        result["asset"] = asset_tf.group(1).upper()
        raw_tf = asset_tf.group(2).upper()
        result["timeframe"] = normalize_timeframe(raw_tf)

    # Side
    side_match = re.search(r'Side:\s*(Support|Resistance)', rest, re.IGNORECASE)
    if side_match:
        result["side"] = side_match.group(1).capitalize()

    # Price
    price_match = re.search(r'Price:\s*([\d.]+)', rest)
    if price_match:
        result["price"] = float(price_match.group(1))

    # Scope
    scope_match = re.search(r'Scope:\s*(Pure|Non-Pure)', rest, re.IGNORECASE)
    if scope_match:
        result["scope"] = scope_match.group(1)

    return result


# ─────────────────────────────────────────────
# SCORING — Confluences selon ta méthode
# ─────────────────────────────────────────────

# Poids des timeframes pour le scoring
TF_WEIGHT = {
    # Petits TF — pas de bonus
    "M1": 0, "M3": 0, "M5": 0, "M10": 0, "M15": 0, "M30": 0, "M45": 0,
    "1M": 0, "3M": 0, "5M": 0, "15M": 0, "30M": 0,
    "30S": 0, "1S": 0,
    # H1/H2 — bonus léger
    "H1": 1, "H2": 1, "1H": 1, "2H": 1,
    # H3/H4/H6/H8/H12 — bonus moyen
    "H3": 2, "H4": 2, "H6": 2, "H8": 2, "H12": 2,
    "4H": 2, "8H": 2, "12H": 2,
    # Daily/Weekly — bonus fort
    "D1": 3, "1D": 3, "D": 3, "DAILY": 3,
    "W1": 3, "1W": 3, "W": 3, "WEEKLY": 3,
    "MN": 3, "MONTHLY": 3,
}

TYPE_SCORES = {
    "origin untouched":        5,   # +3 Origin UNTOUCHED Pure + +2 TF≥Daily (bonus)
    "origin first touch":      4,   # Première visite Origin
    "broken origin first touch": 4,
    "broken first touch":      3,   # Break UNTOUCHED
    "break first touch":       3,
    "break created":           2,
    "origin broken":           2,
    "bsut created":            2,
    "origin touched":          1,
}

def compute_score(parsed: dict) -> dict:
    score = 0
    details = []

    alert_type = (parsed.get("type") or "").lower()
    tf          = (parsed.get("timeframe") or "").upper()
    scope       = (parsed.get("scope") or "").lower()
    side        = (parsed.get("side") or "").lower()

    # Score de base selon le type d'alerte
    base = 0
    for key, val in TYPE_SCORES.items():
        if key in alert_type:
            base = val
            details.append(f"Type '{parsed['type']}' → +{val}")
            break

    score += base

    # Bonus Scope Pure
    if scope == "pure":
        score += 2
        details.append("Scope Pure → +2")

    # Bonus Timeframe
    tf_score = TF_WEIGHT.get(tf, 0)
    if tf_score > 0:
        score += tf_score
        details.append(f"Timeframe {tf} → +{tf_score}")

    # Bonus First Touch (première visite = clé de la méthode)
    if "first touch" in alert_type:
        score += 2
        details.append("Première visite (First Touch) → +2")

    # Niveau prioritaire
    if score >= 8:
        level = "PRIORITAIRE"
        emoji = "🔴"
    elif score >= 5:
        level = "SECONDAIRE"
        emoji = "⚠️"
    else:
        level = "INFO"
        emoji = "📊"

    return {
        "score": score,
        "level": level,
        "emoji": emoji,
        "details": details,
    }


# ─────────────────────────────────────────────
# TELEGRAM
# ─────────────────────────────────────────────
def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[TELEGRAM] Token ou Chat ID manquant — message non envoyé")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[TELEGRAM] Erreur : {e}")
        return False


def format_telegram_message(parsed: dict, scoring: dict) -> str:
    side_emoji = "🟢" if parsed.get("side") == "Support" else "🔴"
    scope_tag  = "✅ Pure" if parsed.get("scope") == "Pure" else "⬜ Non-Pure"

    # Action suggérée
    if parsed.get("side") == "Support":
        action = "→ Surveille M1 maintenant\n→ Setup <b>LONG</b> potentiel\n→ SL visé : 5-10 pts"
    else:
        action = "→ Surveille M1 maintenant\n→ Setup <b>SHORT</b> potentiel\n→ SL visé : 5-10 pts"

    msg = (
        f"{scoring['emoji']} <b>ALERTE {scoring['level']} — Score {scoring['score']}/15</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Asset    : <b>{parsed.get('asset', '?')}</b>\n"
        f"Niveau   : <b>{parsed.get('price', '?')}</b>\n"
        f"Type     : {parsed.get('type', '?')}\n"
        f"TF       : {parsed.get('timeframe', '?')}\n"
        f"Side     : {side_emoji} {parsed.get('side', '?')}\n"
        f"Scope    : {scope_tag}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Scoring détail :\n"
    )

    for d in scoring["details"]:
        msg += f"  • {d}\n"

    msg += (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Action :\n{action}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {parsed.get('timestamp', '')[:19].replace('T', ' ')} UTC"
    )
    return msg


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    """Point d'entrée des alertes TradingView / Fib Lab"""
    # Récupération du body brut
    raw = request.get_data(as_text=True).strip()

    # Essai de parse JSON au cas où TradingView envoie du JSON
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            raw = data.get("message", data.get("text", raw))
        except Exception:
            pass

    print(f"[WEBHOOK] Reçu : {raw}")

    if not raw:
        return jsonify({"error": "empty body"}), 400

    # Parse + Score
    parsed  = parse_fiblab_message(raw)
    scoring = compute_score(parsed)

    # Sauvegarde historique
    entry = {**parsed, **scoring}
    alert_history.appendleft(entry)

    # Envoi Telegram
    tg_msg = format_telegram_message(parsed, scoring)
    sent   = send_telegram(tg_msg)

    print(f"[WEBHOOK] Score={scoring['score']} Level={scoring['level']} Telegram={'✅' if sent else '❌'}")

    return jsonify({
        "status": "ok",
        "parsed": parsed,
        "scoring": scoring,
        "telegram_sent": sent,
    }), 200


@app.route("/status", methods=["GET"])
def status():
    """Health check"""
    return jsonify({
        "status": "running",
        "alerts_received": len(alert_history),
        "telegram_configured": bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID),
        "last_alert": alert_history[0]["timestamp"] if alert_history else None,
    })


@app.route("/levels", methods=["GET"])
def levels():
    """Derniers niveaux actifs"""
    return jsonify(list(alert_history))


@app.route("/", methods=["GET"])
def dashboard():
    """Dashboard HTML"""
    return render_template("dashboard.html", alerts=list(alert_history))


@app.route("/test", methods=["GET"])
def test_alert():
    """Simule une alerte pour tester Telegram"""
    fake = "Origin First Touch — XAUUSD H4 | Side: Support | Price: 3325.00 | Scope: Pure"
    parsed  = parse_fiblab_message(fake)
    scoring = compute_score(parsed)
    tg_msg  = format_telegram_message(parsed, scoring)
    sent    = send_telegram(tg_msg)
    return jsonify({"message": tg_msg, "telegram_sent": sent})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
