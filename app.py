"""
╔══════════════════════════════════════════════════════════════╗
║         FIBLAB ROBOT — Webhook Trading Server  (v2.7.16)     ║
║         Charlie Joe 1972 — Juillet 2026                      ║
║                                                              ║
║  Patch v2.7.16 "Dashboard global + par actif" :              ║
║   • /stats_view?asset=xau|dax|solana|btc|hype|sui|stocks :   ║
║     filtre toute la page sur un groupe d'actifs (puces)      ║
║   • Tableau "par ACTIF" (win rate + espérance R), cliquable, ║
║     visible en vue globale — respecte le filtre TYPE         ║
║                                                              ║
║  Patch v2.7.15 "Ticket ULTIME élargi + log ?asset=" :        ║
║   • mode ultime = H4/H6/H8/H12 (même mécanique Fibo ; edge   ║
║     validé sur l'agrégat Origin Hold ACTIVATED, PAS TF par   ║
║     TF — le dashboard tranchera)                             ║
║   • [WEBHOOK] RAW logge aussi le ?asset= reçu (diagnostic    ║
║     des URL d'alerte mal configurées, token jamais loggé)    ║
║                                                              ║
║  Patch v2.7.14 "Ticker prioritaire + fix TF Daily + garde" : ║
║   • parse 'Ticker: XXX' dans le corps (prioritaire sur       ║
║     ?asset= de l'URL) — hold ET standard                     ║
║   • FIX : regex TF du parser hold tronquait '1D'→'1'→M1      ║
║     (Daily/2D/3D/W jetés comme scalp minute) → capture '1D'  ║
║   • Garde-fou cohérence prix↔actif : ⚠️ visible (Telegram +  ║
║     ticket + log) si le prix sort de la gamme de l'actif.    ║
║     FLAG SEULEMENT, jamais d'auto-correction (gammes crypto  ║
║     se recouvrent → une correction auto serait pire)         ║
║   • Log du payload brut complet ([WEBHOOK] RAW) pour debug   ║
║                                                              ║
║  Base v2.5.1 + patch v2.6.0 "Syn-calibrated scoring" :       ║
║   • TYPE_SCORES re-pondérés sur les probabilités de Syn      ║
║     (retest break level = 95% → poids relevé)                ║
║   • Bonus de CONFLUENCE : niveaux empilés au même prix       ║
║     sur plusieurs TF = haute proba (cœur du système Syn)     ║
║   • Intégration HOLD LEVELS (indicateur Syn) :               ║
║     parser multi-lignes + 6 états + cible d'obligation (Exit)║
║   • Champ target (cible d'obligation) : message + calibration║
║   • Fallback asset via ?asset= dans l'URL du webhook hold    ║
║                                                              ║
║  Patch v2.6.2 "Fib0 stop réel" :                             ║
║   • Stop d'éval des alertes HOLD = Fib0 calculé (bas/haut    ║
║     de la bougie englobée) au lieu du stop ATR à l'aveugle   ║
║   • Repli auto sur l'ATR si bougie manquante / feed KO       ║
║                                                              ║
║  Patch v2.7.13 "SL paramétrable (fraction Fibo)" :           ║
║   • /sl_fib 0.786|0.5|0.382|0|-1 : stop à la fraction Fibo   ║
║     (éval + ticket) ; défaut 0.5 (backtest : ~+0.18R)        ║
║                                                              ║
║  Patch v2.7.12 "Modes de ticket ULTIME / LARGE" :            ║
║   • /ticket_tf ultime (H4 seul) | large (H1..H12+Daily..W)   ║
║   • filtre par label normalisé (distingue H1 de M1)          ║
║                                                              ║
║  Patch v2.7.11 "Verrou H4 + lien TV + /sl_sweep" :           ║
║   • ticket : uniquement H4 + lien TradingView                ║
║   • /sl_sweep : backtest du stop (0.786/0.5/0.382/0/-1)      ║
║     -> % stop touché, R:R, espérance par niveau              ║
║                                                              ║
║  Patch v2.7.10 "Ticket = ordre limite au repos" :            ║
║   • ticket reformaté en ORDRE LIMITE prêt à poser (ligne     ║
║     copier-coller) : pose et pars, zéro surveillance         ║
║                                                              ║
║  MAJEUR v2.7.9 "Fib 0 dérivé de la cible (Exit=1.618)" :     ║
║   • Fib 0 (stop) déduit de Entrée+Exit, EXACT, sans dev ni   ║
║     reconstruction -> R fiable + ticket exact + ladder de TP ║
║   • hypothèse : Exit = TP1 = Fib 1.618 (validé sur chart)    ║
║                                                              ║
║  Patch v2.7.8 "Entrée éval = niveau d'origine (Fib 1)" :     ║
║   • revert v2.7.3 : l'entrée redevient le niveau (Fib 1 =    ║
║     Entry touched), confirmé — cohérent avec le ticket       ║
║   • (R fiable seulement quand le dev livrera Fib 0)          ║
║                                                              ║
║  Patch v2.7.7 "Ticket de trade semi-auto (démo)" :           ║
║   • sur Origin Hold ACTIVATED : ticket Telegram prêt à       ║
║     exécuter (entrée niveau, TP Exit, SL Fib0, taille 1%)    ║
║                                                              ║
║  Patch v2.7.6 "Filtre type sur dashboard" :                  ║
║   • /stats_view?type=hold|bsut|... : chips cliquables pour   ║
║     isoler un type/famille (confort d'analyse)               ║
║                                                              ║
║  Patch v2.7.5 "Toggle /ideal on|off" :                       ║
║   • commande Telegram /ideal on|off (admin) pour activer /   ║
║     couper le filtre idéal sans redéployer ; état dans /status║
║                                                              ║
║  Patch v2.7.4 "Alertes idéales seulement" :                  ║
║   • notification filtrée aux Hold CONFIRMÉS (espérance + )   ║
║     ; tout le reste stocké mais MUET. NOTIFY_ONLY_IDEAL      ║
║                                                              ║
║  Patch v2.7.3 "Entrée Hold = close englobante + stop plancher"║
║   • close des bougies récupéré (4e champ du tuple prix)      ║
║   • entrée Hold = CLÔTURE de l'englobante (confirmation), au ║
║     lieu du niveau -> le proxy n'empoche plus le trajet grat.║
║   • stop Fib0 plancherisé max(sl_floor, 0.5*ATR) -> tue les  ║
║     R gonflés par un stop minuscule ; le R dégonfle vers réel║
║                                                              ║
║  Patch v2.7.2 "R / espérance sur le dashboard" :             ║
║   • cartes R moyen (espérance) + R total globaux             ║
║   • tableau Espérance par type (R moyen, R total) trié       ║
║     par espérance — la vraie mesure, au-delà du win rate     ║
║                                                              ║
║  Patch v2.7.1 "Repli Yahoo aussi sur 429/exception" :        ║
║   • fetch_prices : chaque source dans son propre try ; une   ║
║     exception Twelve Data (429 rate limit) bascule enfin sur ║
║     Yahoo au lieu de tout perdre                             ║
║                                                              ║
║  MAJEUR v2.7.0 "Évaluation par lot" :                        ║
║   • fetch prix UNE fois par ACTIF (au lieu d'un par alerte)  ║
║     → ~7 requêtes au lieu de ~800, fin du mur de quota       ║
║   • logique SL/TP/Fib0 inchangée (slicing en mémoire)        ║
║                                                              ║
║  Patch v2.6.8 "Repli Yahoo si Twelve Data vide" :            ║
║   • fetch_prices bascule sur Yahoo quand Twelve Data renvoie ║
║     vide (quota jour épuisé), pas seulement sur exception    ║
║                                                              ║
║  Patch v2.6.7 "Fix éval : alertes mûres d'abord" :           ║
║   • /evaluate ne charge que les alertes >12h (filtre SQL)    ║
║     → plus de lot gaspillé sur des alertes trop récentes     ║
║                                                              ║
║  Patch v2.6.6 "Dashboard bilingue FR/EN" :                   ║
║   • /stats_view?lang=en + sélecteur de langue sur la page    ║
║                                                              ║
║  Patch v2.6.5 "Export dashboard" :                           ║
║   • /export.csv : dump CSV complet (alertes + issues + R)    ║
║   • Boutons Export CSV / Imprimer-PDF sur /stats_view        ║
║     (+ CSS d'impression, sans dépendance externe)            ║
║                                                              ║
║  Patch v2.6.4 "Éval priorité Hold" :                         ║
║   • /evaluate traite d'abord les alertes HOLD, puis les plus ║
║     récentes (au lieu du plus vieux) → les cases utiles du   ║
║     dashboard se remplissent vite ; le vieux bruit attend    ║
║                                                              ║
║  Patch v2.6.3 "Rescore" :                                    ║
║   • /rescore : recalcule score+niveau de TOUT le stock avec  ║
║     les poids Syn ; confluence reconstruite fidèlement       ║
║     (rejeu des alertes par ordre d'arrivée)                  ║
║                                                              ║
║  Hérité de v2.5.1 :                                          ║
║   • Scoring 6D/7D, persistance, killswitch, /stats_view, etc.║
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
                level     TEXT,
                target    REAL,
                move_pct  REAL
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


def migrate_db():
    """Ajoute les colonnes target/move_pct si la base vient d'une version < 2.6.0.
    Idempotent : ne fait rien si les colonnes existent déjà."""
    try:
        with db() as conn:
            cols = [r["name"] for r in conn.execute("PRAGMA table_info(alerts)")]
            if "target" not in cols:
                conn.execute("ALTER TABLE alerts ADD COLUMN target REAL")
            if "move_pct" not in cols:
                conn.execute("ALTER TABLE alerts ADD COLUMN move_pct REAL")
            conn.commit()
    except Exception as e:
        print(f"[DB] migrate_db : {e}")


def save_alert(parsed: dict, scoring: dict, group: str) -> int:
    """Insère l'alerte + une ligne 'pending' dans outcomes. Retourne l'id."""
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO alerts (ts,asset,grp,timeframe,type,side,price,scope,score,level,target,move_pct) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (parsed.get("timestamp"), parsed.get("asset"), group, parsed.get("timeframe"),
             parsed.get("type"), parsed.get("side"), parsed.get("price"), parsed.get("scope"),
             scoring["score"], scoring["level"], parsed.get("target"), parsed.get("move_pct"))
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
    "hype":   {"HYPEUSDT", "HYPEUSDT.P", "HYPEUSD", "HYPE"},
    "sui":    {"SUIUSDT", "SUIUSDT.P", "SUIUSD", "SUI"},
    "stocks": {"TSLA", "HOOD", "CELH", "TTD", "PLTR", "AMZN", "NVDA", "AAPL", "META", "GOOGL", "MSFT", "SOFI"},
}

ASSET_META = {
    "xau":    {"label": "XAU/USD", "emoji": "🥇", "tv": "https://www.tradingview.com/chart/?symbol=OANDA:XAUUSD"},
    "dax":    {"label": "DAX",     "emoji": "🇩🇪", "tv": "https://www.tradingview.com/chart/?symbol=OANDA:DE30EUR"},
    "solana": {"label": "SOLANA",  "emoji": "💎", "tv": "https://www.tradingview.com/chart/?symbol=BITGET:SOLUSDT.P"},
    "btc":    {"label": "BITCOIN", "emoji": "₿",  "tv": "https://www.tradingview.com/chart/?symbol=BITGET:BTCUSDT.P"},
    "hype":   {"label": "HYPE",    "emoji": "🚀", "tv": "https://www.tradingview.com/chart/?symbol=BITGET:HYPEUSDT.P"},
    "sui":    {"label": "SUI",     "emoji": "🌊", "tv": "https://www.tradingview.com/chart/?symbol=BITGET:SUIUSDT.P"},
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


# v2.7.14 — Garde-fou cohérence prix↔actif. Gammes HEURISTIQUES larges (à
# ajuster si un actif migre). FLAG SEULEMENT : pas d'auto-correction, car les
# gammes crypto se recouvrent (SOL~79, HYPE~66) → corriger à l'aveugle serait
# pire que signaler. But : attraper un XAU à 4106 étiqueté SOLUSDT.P.
PRICE_RANGES = {
    "xau":    (1500, 8000),
    "dax":    (8000, 60000),
    "solana": (10, 2000),
    "btc":    (10000, 1000000),
    "hype":   (0.5, 500),
    "sui":    (0.05, 50),
}


def asset_coherence_warning(parsed: dict, group: str):
    """None si cohérent/inconnu ; sinon un texte d'alerte (prix hors gamme
    de l'actif étiqueté → probable mauvais ?asset= ou alerte mal configurée)."""
    try:
        price = parsed.get("price")
        rng = PRICE_RANGES.get(group)
        if price is None or rng is None:
            return None
        lo, hi = rng
        if lo <= float(price) <= hi:
            return None
        return (f"prix {price} hors gamme {group.upper()} [{lo}\u2013{hi}] "
                f"\u2014 actif probablement MAL \u00c9TIQUET\u00c9 (v\u00e9rifie ?asset=/Ticker)")
    except Exception:
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


# ── rechargement de l'historique au démarrage ──
LEVEL_EMOJI = {"PRIORITAIRE": "🔴", "SECONDAIRE": "⚠️", "INFO": "📊"}


def load_alert_history(limit: int = 200):
    """Recharge les dernières alertes depuis SQLite au démarrage.
    Sans ça, le dashboard repart vide à chaque redéploiement même si la
    base persiste."""
    try:
        with db() as conn:
            rows = conn.execute(
                "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        for r in reversed(rows):          # plus ancien → plus récent
            keys = r.keys()
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
                "target":    r["target"]   if "target"   in keys else None,
                "move_pct":  r["move_pct"] if "move_pct" in keys else None,
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


def parse_hold_message(raw: str, asset_hint: str = None) -> dict:
    """Parse le format multi-lignes Hold/Origin Hold de l'indicateur Syn.
    Retourne None si ce n'est pas un message hold (laisse la main au parser std).
    Le champ 'Exit' devient la cible d'obligation (target)."""
    lines = [l.strip() for l in raw.replace("\\n", "\n").split("\n") if l.strip()]
    # v2.7.14 : une éventuelle ligne 'Ticker: XXX' en tête ne doit pas masquer
    # la détection du type hold — le type = première ligne NON-Ticker.
    type_lines = [l for l in lines if not l.lower().startswith("ticker:")]
    if not type_lines or "hold" not in type_lines[0].lower():
        return None
    res = {"raw": raw.strip(), "type": type_lines[0].strip(), "asset": None,
           "timeframe": None, "side": None, "price": None, "target": None,
           "move_pct": None, "scope": "Pure", "timestamp": now_iso()}
    body = "\n".join(lines)

    # v2.7.14 FIX : capturer '1D'/'3D'/'1W' entiers (l'ancien \d+ tronquait
    # '1D' en '1' → normalisé M1 → Daily jeté comme scalp minute).
    m = re.search(r"TF:\s*([0-9]+[A-Za-z]*)", body)
    if m:
        res["timeframe"] = normalize_timeframe(m.group(1).upper())
    for l in lines:
        if l in ("Support", "Resistance"):
            res["side"] = l
    m = (re.search(r"Entry touched:\s*([\d.]+)", body)
         or re.search(r"Entry:\s*([\d.]+)", body)
         or re.search(r"entry nearby:\s*([\d.]+)", body))
    if m:
        res["price"] = float(m.group(1))
    m = re.search(r"Exit:\s*([\d.]+)", body)          # cible d'obligation
    if m:
        res["target"] = float(m.group(1))
    m = re.search(r"Move%:\s*([\d.]+)", body)
    if m:
        res["move_pct"] = float(m.group(1))
    # v2.7.14 : le ticker du CORPS ('Ticker: XAUUSD') prime sur le ?asset= de
    # l'URL (source du bug XAU étiqueté SOLUSDT.P — URL partagée mal configurée).
    m = re.search(r"^Ticker:\s*([A-Za-z0-9./!_:-]+)", body, re.MULTILINE)
    if m:
        res["asset"] = m.group(1).upper()
    elif asset_hint:
        res["asset"] = asset_hint.upper()
    return res


def parse_fiblab_message(raw: str) -> dict:
    result = {
        "raw": raw.strip(), "type": None, "asset": None,
        "timeframe": None, "side": None, "price": None,
        "scope": None, "target": None, "move_pct": None,
        "timestamp": now_iso(),
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
    m = re.search(r'Target:\s*([\d.]+)', rest, re.IGNORECASE)   # cible optionnelle (pipe)
    if m:
        result["target"] = float(m.group(1))
    # v2.7.14 : 'Ticker: XXX' dans le corps prime sur l'asset détecté par regex.
    m = re.search(r"^Ticker:\s*([A-Za-z0-9./!_:-]+)", raw, re.MULTILINE)
    if m:
        result["asset"] = m.group(1).upper()
    return result


# ─────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────
TF_WEIGHT = {
    "M1": 0, "M2": 0, "M3": 0, "M4": 0, "M5": 1, "M10": 1, "M15": 1, "M30": 1, "M45": 1,
    "H1": 2, "H2": 2, "H3": 2,
    "H4": 3, "H6": 3, "H8": 3, "H12": 3,
    "D1": 4, "1D": 4, "D": 4, "DAILY": 4,
    "2D": 4, "3D": 5, "4D": 5, "5D": 5,
    "D2": 4, "D3": 5, "D4": 5, "D5": 5,
    "6D": 5, "7D": 5, "D6": 5, "D7": 5,
    "W1": 4, "1W": 4, "W": 4, "WEEKLY": 4, "MN": 4, "MONTHLY": 4,
    "72m": 1, "90m": 1, "96m": 1, "144m": 2, "160m": 2, "288m": 2,
}

# Poids fondés sur la hiérarchie de probabilité de Syn (corpus) :
#   retest break level cassé ~95% · hold rejection / untested origin ~90% ·
#   origin retest 1ère visite haute · formation faible.
# Ce sont des PRIORS : /stats_view reste l'arbitre sur tes vrais trades.
TYPE_SCORES = {
    # — retest de niveau cassé : catégorie la + fiable (95%) —
    "break first touch":           6,
    "broken first touch":          6,
    # — origin retest première visite (~90%) —
    "broken origin first touch":   5,
    "origin first touch":          5,
    "origin untouched":            5,
    # — HOLD LEVELS (indicateur Syn) : rejet de hold = proba la + haute —
    "hold activated":              6,   # attrape aussi "Origin Hold ACTIVATED"
    "hold armed":                  4,   # "Origin Hold ARMED"
    "hold atr proximity":          3,   # "Hold/Origin Hold ATR PROXIMITY"
    "hold created":                2,   # niveau formé, prix pas encore là
    # — approche / armement —
    "atr proximity":               3,
    # — niveau déjà visité —
    "origin touched":              1,
    # — flips / BSUT (valider Syn) —
    "origin broken: origin bsut created": 3,
    "break broken: bsut created":  3,
    # — événements de FORMATION —
    "rng-hit created":             2,
    "origin created":              1,
    "break created":               1,
    # — fallbacks —
    "origin broken":               2,
    "bsut created":                2,
}


# ── CONFLUENCE : niveaux empilés au même prix = haute proba (système Syn) ──
CONFLUENCE_TOL_PCT = 0.8      # tolérance prix pour considérer deux niveaux "au même endroit"
CONFLUENCE_MAX_BONUS = 4      # plafond du bonus


def confluence_bonus(parsed: dict, history, tol_pct: float = CONFLUENCE_TOL_PCT,
                     max_bonus: int = CONFLUENCE_MAX_BONUS):
    """(bonus, details) : compte les alertes récentes de même asset+side, à prix
    proche, sur des TF DIFFÉRENTS (un même TF ne compte qu'une fois)."""
    asset = (parsed.get("asset") or "").upper()
    side  = parsed.get("side")
    price = parsed.get("price")
    tf    = parsed.get("timeframe")
    if not (asset and side and price):
        return 0, []
    stacked, seen_tf = [], set()
    for h in history:
        if (h.get("asset") or "").upper() != asset:
            continue
        if h.get("side") != side:
            continue
        htf = h.get("timeframe")
        if htf == tf or htf in seen_tf:
            continue
        hp = h.get("price")
        if hp and abs(price - hp) / hp * 100 <= tol_pct:
            stacked.append(htf)
            seen_tf.add(htf)
    n = len(stacked)
    if n == 0:
        return 0, []
    bonus = min(n + 1, max_bonus)          # 1 empilement → +2, 2 → +3, 3+ → +4
    return bonus, [f"Confluence ×{n} (TF empilés : {', '.join(map(str, stacked))}) → +{bonus}"]


def compute_score(parsed: dict, history=None) -> dict:
    score, details = 0, []
    alert_type = (parsed.get("type") or "").lower()
    tf    = (parsed.get("timeframe") or "").upper()
    scope = (parsed.get("scope") or "").lower()

    for key in sorted(TYPE_SCORES, key=len, reverse=True):
        if key in alert_type:
            val = TYPE_SCORES[key]
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

    # ── CONFLUENCE (si l'historique est fourni) ──
    if history is not None:
        cb, cdetails = confluence_bonus(parsed, history)
        if cb:
            score += cb
            details.extend(cdetails)

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
                    "break first touch", "broken first touch", "broken origin first touch",
                    "hold activated"}
TYPES_DAILY_ONLY = {"origin touched"}
TYPES_SCORE_MIN  = {"bsut created": 6}
TYPES_IGNORED    = {"break created"}

# ── Filtre "alertes idéales" ──────────────────────────────────
# Ne notifier QUE les types à espérance positive prouvée par la calibration :
# les Hold CONFIRMÉS (Hold ACTIVATED + Origin Hold ACTIVATED). Tout le reste
# (First Touch, BSUT, Created, ARMED, PROXIMITY, RNG-HIT...) reste STOCKÉ pour
# la calibration mais MUET côté Telegram. False = ancien comportement permissif.
# "hold activated" (substring) couvre Hold ACTIVATED ET Origin Hold ACTIVATED.
NOTIFY_ONLY_IDEAL = True
TYPES_IDEAL       = {"hold activated"}
robot_state["notify_only_ideal"] = NOTIFY_ONLY_IDEAL   # état runtime (toggle /ideal)

# ── Ticket de trade (semi-auto démo) ──────────────────────────
# Sur les types tradeables (Origin Hold ACTIVATED), le bot envoie à l'admin un
# ticket prêt : entrée = niveau (exact), TP = Exit (exact), SL = Fib0 reconstruit,
# taille pour un risque fixe. Démo, pour se faire la main avant tout auto réel.
TICKET_ENABLED   = True
TICKET_CAPITAL   = 100000.0                    # capital démo (USD)
TICKET_RISK_PCT  = 1.0                          # risque par trade (% du capital)
TICKET_TYPES     = {"origin hold activated"}
# Valeur du point PAR LOT, par actif — HYPOTHÈSES à VÉRIFIER selon ton broker !
CONTRACT_VALUE   = {"xau": 100.0, "dax": 25.0, "btc": 1.0, "solana": 1.0,
                    "hype": 1.0, "sui": 1.0, "stocks": 1.0}
CONTRACT_DEFAULT = 1.0
STOP_FIB_LEVELS  = [0.786, 0.5, 0.382, 0.0, -1.0]   # sweep SL : 0.786=serré -> -1=large
# Deux modes de TF pour le ticket (bascule /ticket_tf) :
#  - ultime : H4/H6/H8/H12 (swing intraday ; edge validé sur l'agrégat,
#    pas TF par TF) — défaut, pour la semaine
#  - large  : H1..H12 + Daily..Weekly (plus d'opportunités, non validées hors H4)
# Filtre par LABEL normalisé (et non tf_hours, qui confond H1 et M1).
TICKET_TF_ULTIME = {"H4", "H6", "H8", "H12"}   # v2.7.15 : swing intraday complet
TICKET_TF_LARGE  = {"H1", "H2", "H4", "H6", "H8", "H12",
                    "D1", "1D", "D", "DAILY", "2D", "3D", "4D", "5D", "6D", "7D",
                    "D2", "D3", "D4", "D5", "D6", "D7", "W1", "1W", "W", "WEEKLY"}
robot_state["ticket_tf_mode"] = "ultime"        # état runtime (bascule /ticket_tf)
# Fraction Fibo du STOP (éval + ticket), réglable via /sl_fib :
#  0 = Fib 0 (large) · 0.382/0.5 = intermédiaire · 0.786 = serré · -1 = très large
# Backtest /sl_sweep : le stop serré maximise l'espérance (0.5 ~+0.18R tenable).
SL_FIB_DEFAULT = 0.5
robot_state["sl_fib"] = SL_FIB_DEFAULT


def _ticket_tf_set():
    return TICKET_TF_LARGE if robot_state.get("ticket_tf_mode") == "large" else TICKET_TF_ULTIME


def _ticket_tf_ok(tf):
    return normalize_timeframe(str(tf or "").strip()).upper() in _ticket_tf_set()


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

    # ── Alertes idéales : seuls les Hold confirmés passent (le reste = bruit,
    #    stocké mais muet). Court-circuite toute la logique permissive ci-dessous.
    if robot_state.get("notify_only_ideal", NOTIFY_ONLY_IDEAL):
        if any(t in alert_type for t in TYPES_IDEAL):
            return True, "ok (idéal)"
        return False, "non idéal (bruit filtré)"

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
    """Envoi Telegram avec retry + backoff (sans dépendance externe)."""
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

    # Ligne cible : si une cible d'obligation est fournie (Exit du hold ou Target),
    # on l'affiche à la place du SL générique.
    target   = parsed.get("target")
    move_pct = parsed.get("move_pct")
    if target:
        tgt_line = f"→ 🎯 Cible obligation : <b>{esc(target)}</b>"
        if move_pct:
            tgt_line += f"  (<b>{esc(move_pct)}%</b>)"
    else:
        tgt_line = "→ SL visé : 5-10 pts"

    action = (
        f"→ Surveille M1 maintenant\n→ Setup <b>LONG</b> potentiel\n{tgt_line}"
        if parsed.get("side") == "Support" else
        f"→ Surveille M1 maintenant\n→ Setup <b>SHORT</b> potentiel\n{tgt_line}"
    )

    # v2.7.14 : avertissement de cohérence prix↔actif, bien visible
    coh_line = ""
    if parsed.get("_coherence_warn"):
        coh_line = f"\u26a0\ufe0f <b>{esc(parsed['_coherence_warn'])}</b>\n"

    msg = (
        f"{scoring['emoji']} <b>ALERTE {scoring['level']} — Score {scoring['score']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{coh_line}"
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

    elif cmd == "/ideal":
        if chat_id != TELEGRAM_CHAT_ID:
            msg = "⛔ Commande réservée à l'admin."
        elif arg == "on":
            robot_state["notify_only_ideal"] = True
            msg = ("🎯 <b>Filtre IDÉAL ON</b> — seuls les Hold confirmés "
                   "(Hold ACTIVATED + Origin Hold ACTIVATED) sont notifiés.\n"
                   "Le reste reste stocké pour la calibration, mais muet.")
        elif arg == "off":
            robot_state["notify_only_ideal"] = False
            msg = ("📢 <b>Filtre IDÉAL OFF</b> — le filtre standard (score + TF) "
                   "reprend la main. Attention au flot d'alertes.")
        else:
            etat = "ON 🎯" if robot_state.get("notify_only_ideal", NOTIFY_ONLY_IDEAL) else "OFF 📢"
            msg = (f"Filtre alertes idéales : <b>{etat}</b>\n"
                   f"Types notifiés : {', '.join(sorted(TYPES_IDEAL))}\n"
                   f"Usage : /ideal on | /ideal off")

    elif cmd == "/ticket_tf":
        if chat_id != TELEGRAM_CHAT_ID:
            msg = "\u26d4 Commande réservée à l'admin."
        elif arg in ("ultime", "ultimate", "h4"):
            robot_state["ticket_tf_mode"] = "ultime"
            msg = ("\U0001F3AF <b>Tickets : ULTIME</b> \u2014 H4/H6/H8/H12 (swing intraday).\n"
                   "Pose et pars, pour la semaine au bureau.")
        elif arg == "large":
            robot_state["ticket_tf_mode"] = "large"
            msg = ("\U0001F310 <b>Tickets : LARGE</b> \u2014 H1/H2/H4/H6/H8/H12 + Daily\u2192Weekly.\n"
                   "Plus d'opportunit\u00e9s (non valid\u00e9es hors H4) \u2014 pour les jours off.")
        else:
            etat = "LARGE \U0001F310" if robot_state.get("ticket_tf_mode") == "large" else "ULTIME \U0001F3AF"
            msg = (f"Tickets TF : <b>{etat}</b>\n"
                   f"Usage : /ticket_tf ultime | /ticket_tf large")

    elif cmd == "/sl_fib":
        if chat_id != TELEGRAM_CHAT_ID:
            msg = "\u26d4 Commande réservée à l'admin."
        else:
            try:
                v = float(arg.replace(",", "."))
            except ValueError:
                v = None
            if v is not None and -2.0 <= v < 1.0:
                robot_state["sl_fib"] = v
                rr = round(0.618 / (1.0 - v), 2) if (1.0 - v) != 0 else 0.0
                msg = (f"\U0001F3AF <b>Stop = Fib {v:g}</b> (éval + ticket)\n"
                       f"R:R sur TP1 = 1:{rr}\n"
                       f"0 = Fib 0 large \u00b7 0.5 = mi-chemin \u00b7 0.786 = serré\n"
                       f"(fais /reeval pour recalculer le dashboard à ce stop)")
            else:
                cur = robot_state.get("sl_fib", SL_FIB_DEFAULT)
                msg = (f"Stop actuel : <b>Fib {cur:g}</b>\n"
                       f"Usage : /sl_fib 0.786 | 0.5 | 0.382 | 0 | -1")

    elif cmd == "/status":
        tf_on = [k for k, v in profile["tf_custom"].items() if v]
        etat  = "⏸ PAUSE" if profile["paused"] else "✅ ACTIF"
        kill  = "🛑 KILLSWITCH ON" if robot_state["paused"] else ""
        msg = (
            f"🤖 <b>Ton profil FibLab Robot</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"État   : {etat} {kill}\n"
            f"Mode   : <b>{profile['mode'].upper()}</b>\n"
            f"Idéal  : {'🎯 ON' if robot_state.get('notify_only_ideal', NOTIFY_ONLY_IDEAL) else '📢 OFF'}\n"
            f"Tickets: {'\U0001F310 LARGE' if robot_state.get('ticket_tf_mode') == 'large' else '\U0001F3AF ULTIME (H4-H12)'}\n"
            f"Stop   : Fib {robot_state.get('sl_fib', SL_FIB_DEFAULT):g}\n"
            f"TF+    : {', '.join(tf_on) if tf_on else 'aucun'}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Alertes globales : {len(alert_history)}\n"
            f"🥇 XAU : {len(histories['xau'])}\n"
            f"💎 SOL : {len(histories['solana'])}\n"
            f"₿ BTC  : {len(histories['btc'])}\n"
            f"🇩🇪 DAX: {len(histories['dax'])}\n"
            f"🚀 HYPE: {len(histories['hype'])}\n"
            f"🌊 SUI : {len(histories['sui'])}\n"
            f"📈 STK : {len(histories['stocks'])}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"/mode swing|scalp|both\n"
            f"/tf_on 72 | /tf_off 72 | /tf_status\n"
            f"/pause | /reprendre\n"
            f"/ideal on|off\n"
            f"/ticket_tf ultime|large\n"
            f"/sl_fib 0.786|0.5|0|-1"
        )

    elif cmd in ("/derniere", "/xau", "/solana", "/dax", "/btc", "/hype", "/sui", "/stocks"):
        key    = cmd[1:] if cmd[1:] in histories else None
        hist   = histories[key] if key else alert_history
        labels = {"xau": "🥇 XAU", "solana": "💎 Solana", "dax": "🇩🇪 DAX", "btc": "₿ BTC",
                  "hype": "🚀 HYPE", "sui": "🌊 SUI", "stocks": "📈 Stocks"}
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

    try:
        save_profile(chat_id, profile)
    except Exception as e:
        print(f"[DB] save_profile : {e}")

    send_telegram(msg, chat_id)


# ─────────────────────────────────────────────
# ÉVALUATION AUTOMATIQUE DES ISSUES
# ─────────────────────────────────────────────
TWELVEDATA_API_KEY = os.environ.get("TWELVEDATA_API_KEY", "")

EVAL_MIN_AGE_H      = 12
EVAL_ATR_BARS       = 14
EVAL_HORIZON_BARS   = 12
EVAL_HORIZON_MIN_H  = 48
EVAL_HORIZON_MAX_H  = 504
EVAL_LOOKBACK_MAX_H = 504

EVAL_RISK = {
    "xau":    {"k": 2.0, "tp_r": 3.0, "sl_floor": 3.0,  "sl_cap": 150.0,  "fallback": 15.0},
    "dax":    {"k": 2.0, "tp_r": 3.0, "sl_floor": 8.0,  "sl_cap": 400.0,  "fallback": 30.0},
    "btc":    {"k": 2.0, "tp_r": 3.0, "sl_floor": 80.0, "sl_cap": 6000.0, "fallback": 400.0},
    "solana": {"k": 2.0, "tp_r": 3.0, "sl_floor": 0.5,  "sl_cap": 40.0,   "fallback": 2.0},
    "hype":   {"k": 2.0, "tp_r": 3.0, "sl_floor": 0.3,  "sl_cap": 30.0,   "fallback": 1.5},
    "sui":    {"k": 2.0, "tp_r": 3.0, "sl_floor": 0.05, "sl_cap": 5.0,    "fallback": 0.3},
    "stocks": {"k": 2.0, "tp_r": 3.0, "sl_floor": 0.3,  "sl_cap": 60.0,   "fallback": 2.0},
}

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


def _fib0_from_target(entry, target, long_bias):
    """Déduit Fib 0 (le stop) de l'entrée (Fib 1) et de la cible d'obligation
    (Exit = Fib 1.618). Le Fibo est une structure à ratio fixe : 1 unité =
    |cible - entrée| / 0.618 ; Fib 0 = entrée + 1 unité du côté OPPOSÉ à la cible
    (le côté du stop). Exact, sans reconstruction. None si données incohérentes."""
    if entry is None or target is None:
        return None
    if long_bias and target <= entry:
        return None
    if (not long_bias) and target >= entry:
        return None
    unit = abs(target - entry) / 0.618
    if unit <= 0:
        return None
    return (entry - unit) if long_bias else (entry + unit)


def _stop_from_fib(entry, target, long_bias, f):
    """Prix du stop à la fraction Fibo f entre l'entrée (Fib 1) et le Fib 0.
    f=0 -> Fib 0 (large) ; 0.5 -> mi-chemin ; 0.786 -> serré ; -1 -> au-delà du
    Fib 0. Dérivé de l'entrée + la cible (Exit=Fib 1.618). None si incohérent."""
    if entry is None or target is None:
        return None
    if long_bias and target <= entry:
        return None
    if (not long_bias) and target >= entry:
        return None
    unit = abs(target - entry) / 0.618
    dist = (1.0 - f) * unit
    if dist <= 0:
        return None
    return (entry - dist) if long_bias else (entry + dist)


def _fib0_from_bars(pre_bars, ts, tf_h, long_bias):
    """Fib0 = extrême de la bougie ENGLOBÉE (celle juste avant la bougie de
    signal, qui se clôture ~à ts). Fenêtre d'un TF précédant le signal.
    Long → son low ; Short → son high. Reconstruit depuis les H1 (approx :
    dépend du feed / de l'alignement de session). None si fenêtre vide."""
    if not pre_bars:
        return None
    hi_bound = ts - timedelta(hours=tf_h)
    lo_bound = ts - timedelta(hours=2 * tf_h)
    window = [b for b in pre_bars if lo_bound < b[0] <= hi_bound]
    if not window:
        return None
    return min(b[2] for b in window) if long_bias else max(b[1] for b in window)


SYMBOL_MAP_YF = {"xau": "GC=F", "dax": "^GDAXI", "btc": "BTC-USD", "solana": "SOL-USD",
                 "hype": "HYPE-USD", "sui": "SUI-USD"}
SYMBOL_MAP_TD = {"xau": "XAU/USD", "dax": "DAX", "btc": "BTC/USD", "solana": "SOL/USD",
                 "hype": "HYPE/USD", "sui": "SUI/USD"}


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
    highs, lows, closes = q.get("high") or [], q.get("low") or [], q.get("close") or []
    bars = []
    for i, t in enumerate(ts):
        hi = highs[i] if i < len(highs) else None
        lo = lows[i] if i < len(lows) else None
        cl = closes[i] if i < len(closes) else None
        if hi is not None and lo is not None:
            bars.append((datetime.fromtimestamp(t, tz=timezone.utc), float(hi), float(lo),
                         float(cl) if cl is not None else float(hi)))
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
            bars.append((dt, float(v["high"]), float(v["low"]), float(v["close"])))
        except Exception:
            continue
    bars.sort(key=lambda x: x[0])
    return bars


def fetch_prices(group, asset, start_dt, end_dt):
    """[(datetime, high, low), ...] en H1. Twelve Data si clé, avec REPLI Yahoo
    dès que Twelve Data ÉCHOUE ou renvoie vide — y compris sur 429 (rate limit).
    Chaque source est isolée dans son propre try : une exception Twelve Data ne
    saute plus par-dessus le repli Yahoo (bug < v2.7.1)."""
    bars = []
    if TWELVEDATA_API_KEY:
        sym = _twelvedata_symbol(group, asset)
        if sym:
            try:
                bars = _fetch_twelvedata(sym, start_dt, end_dt)
            except Exception as e:
                print(f"[EVAL] twelvedata {group}/{asset} : {e}")
                bars = []
    if bars:
        return bars
    # Twelve Data vide ou en échec (429 / quota) -> on tente Yahoo
    sym = _yahoo_symbol(group, asset)
    if sym:
        try:
            return _fetch_yahoo(sym, start_dt, end_dt)
        except Exception as e:
            print(f"[EVAL] yahoo {group}/{asset} : {e}")
    return []


def evaluate_pending_outcomes():
    """Évalue les alertes 'pending' — ÉVALUATION PAR LOT (v2.7.0).
    Au lieu d'un fetch de prix par alerte, on récupère l'historique de chaque
    ACTIF une seule fois, puis on évalue toutes ses alertes en attente depuis ce
    même jeu de données (~7 requêtes au lieu de ~800 → fin du problème de quota).
    Stop Fib0 pour les Hold (sinon ATR adaptatif) ; TP = cible d'obligation si
    connue. Ordre : Hold d'abord, puis plus récentes ; seules les alertes mûres
    (>= EVAL_MIN_AGE_H) sont chargées."""
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(hours=EVAL_MIN_AGE_H)).isoformat()
    with db() as conn:
        rows = conn.execute(
            "SELECT a.id, a.ts, a.asset, a.grp, a.side, a.price, a.timeframe, a.target, a.type "
            "FROM alerts a JOIN outcomes o ON a.id = o.alert_id "
            "WHERE o.status = 'pending' AND a.price IS NOT NULL AND a.side IS NOT NULL "
            "AND a.ts <= ? "
            "ORDER BY (CASE WHEN LOWER(a.type) LIKE '%hold%' THEN 0 ELSE 1 END), a.id DESC "
            "LIMIT 500",
            (cutoff,)
        ).fetchall()

    # Prépare et groupe les alertes par actif, en conservant l'ordre de priorité.
    groups, order = {}, []
    for r in rows:
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
        key = (r["grp"], r["asset"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append({"r": r, "ts": ts, "risk": risk, "tf_h": tf_h,
                            "horizon_h": horizon_h, "lookback_h": lookback_h})

    evaluated = 0
    _start = time.monotonic()
    for key in order:
        if time.monotonic() - _start > 18:      # garde-fou timeout (fetch + marge)
            break
        grp, asset = key
        items = groups[key]
        # UN SEUL fetch pour tout l'actif : du plus ancien besoin jusqu'à maintenant.
        earliest = min(it["ts"] - timedelta(hours=it["lookback_h"]) for it in items)
        floor_dt = now - timedelta(hours=EVAL_LOOKBACK_MAX_H + EVAL_HORIZON_MAX_H)
        bars = fetch_prices(grp, asset, max(earliest, floor_dt), now)
        if not bars:
            continue

        updates = []
        for it in items:
            r = it["r"]; ts = it["ts"]; risk = it["risk"]; tf_h = it["tf_h"]
            horizon_h = it["horizon_h"]
            lb_start = ts - timedelta(hours=it["lookback_h"])
            end_win  = min(ts + timedelta(hours=horizon_h), now)
            # même fenêtre pre/post que l'éval par alerte → ATR/Fib0 identiques
            pre  = [b for b in bars if lb_start <= b[0] <= ts]
            post = [b for b in bars if ts < b[0] <= end_win]
            if not post:
                continue

            atr = _atr_at_tf(pre, tf_h)
            long_bias = (r["side"] == "Support")
            is_hold = "hold" in (r["type"] or "").lower()

            # Entrée = niveau d'origine (Fib 1 = "Entry touched"). Confirmé : Fred
            # entre à l'origine, PAS à la close de l'englobante (revert v2.7.3).
            entry = r["price"]

            # ── STOP ── Hold : Fib 0 DÉRIVÉ de la cible (Exit = Fib 1.618) = stop
            #    EXACT. Repli sur la reconstruction H1 (plancherisée) si pas de cible.
            sl, sl_src = None, None
            if is_hold:
                _slf = robot_state.get("sl_fib", SL_FIB_DEFAULT)
                stop_px = _stop_from_fib(entry, r["target"], long_bias, _slf)
                if stop_px is not None:
                    raw_sl = (entry - stop_px) if long_bias else (stop_px - entry)
                    if raw_sl > 0:
                        sl, sl_src = raw_sl, "fib" + ("%g" % _slf)   # stop à la fraction choisie
                if sl is None:
                    fib0 = _fib0_from_bars(pre, ts, tf_h, long_bias)
                    if fib0 is not None and entry:
                        raw_sl = (entry - fib0) if long_bias else (fib0 - entry)
                        if raw_sl > 0:
                            floor = max(risk["sl_floor"], 0.5 * atr) if (atr and atr > 0) else risk["sl_floor"]
                            sl, sl_src = min(max(raw_sl, floor), risk["sl_cap"]), "fib0~"
            if sl is None:
                if atr and atr > 0:
                    sl, sl_src = min(max(risk["k"] * atr, risk["sl_floor"]), risk["sl_cap"]), "atr"
                else:
                    sl, sl_src = risk["fallback"], "fallback"

            # TP = cible d'obligation réelle si connue, sinon multiple de R.
            if r["target"] is not None and entry:
                tp, tp_src = abs(r["target"] - entry), "obligation"
            else:
                tp, tp_src = sl * risk["tp_r"], "R"

            mfe = mae = 0.0
            status = None
            r_real = None
            for (_dt, hi, lo, _c) in post:
                fav = (hi - entry) if long_bias else (entry - lo)
                adv = (entry - lo) if long_bias else (hi - entry)
                mfe = max(mfe, fav)
                mae = max(mae, adv)
                if adv >= sl:
                    status, r_real = "loss", -1.0
                    break
                if fav >= tp:
                    status, r_real = "win", round(tp / sl, 2) if sl else None
                    break

            if status is None:
                if now >= ts + timedelta(hours=horizon_h):
                    status, r_real = "invalid", (round(mfe / sl, 2) if sl else None)
                else:
                    continue

            src = "twelvedata" if TWELVEDATA_API_KEY else "yahoo"
            note = (f"auto ({src}, TF={r['timeframe']}, SL={round(sl, 2)}[{sl_src}], "
                    f"TP={round(tp, 2)}[{tp_src}], H={int(horizon_h)}h)")
            updates.append((status, round(mfe, 2), round(mae, 2), r_real, note, now_iso(), r["id"]))

        if updates:
            with db() as conn:
                conn.executemany(
                    "UPDATE outcomes SET status=?, mfe_pts=?, mae_pts=?, r_realized=?, "
                    "note=?, updated_ts=? WHERE alert_id=?",
                    updates
                )
                conn.commit()
            evaluated += len(updates)
    return evaluated


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
def build_trade_ticket(parsed, group):
    """ORDRE LIMITE au repos pour les types tradeables (Origin Hold ACTIVATED) :
    limite \u00e0 l'entr\u00e9e (Fib 1), SL = Fib 0 d\u00e9riv\u00e9, ladder de TP d\u00e9riv\u00e9e,
    taille pour un risque fixe. Format pr\u00eat \u00e0 poser, z\u00e9ro surveillance. None si N/A."""
    atype = (parsed.get("type") or "").lower()
    if not any(t in atype for t in TICKET_TYPES):
        return None
    if not _ticket_tf_ok(parsed.get("timeframe")):
        return None
    entry  = parsed.get("price")
    target = parsed.get("target")
    side   = parsed.get("side")
    if entry is None or not side:
        return None
    long_bias = (side == "Support")
    risk_usd  = TICKET_CAPITAL * TICKET_RISK_PCT / 100.0
    slf = robot_state.get("sl_fib", SL_FIB_DEFAULT)
    sl = _stop_from_fib(entry, target, long_bias, slf)
    asset = esc(parsed.get("asset") or "?")
    tf    = esc(parsed.get("timeframe") or "?")
    typ   = esc(parsed.get("type") or "")
    dir_txt = "\U0001F7E2 LONG (achat)" if long_bias else "\U0001F534 SHORT (vente)"
    hdr = ["\U0001F4CB <b>ORDRE LIMITE</b> \u2014 d\u00e9mo " + str(int(TICKET_CAPITAL / 1000)) + "k",
           "<b>" + asset + "</b> \u00b7 TF " + tf + " \u00b7 " + typ]
    # v2.7.14 : cohérence prix↔actif — NE PAS poser cet ordre sans vérifier
    if parsed.get("_coherence_warn"):
        hdr.append("\u26a0\ufe0f <b>" + esc(parsed["_coherence_warn"])
                   + "</b> \u2014 NE PAS POSER sans v\u00e9rifier l'actif")

    if sl is None or target is None:
        return "\n".join(hdr + [
            "\u2501" * 20,
            "Sens   : " + dir_txt,
            "Entr\u00e9e : <b>" + str(entry) + "</b> <i>(Fib 1)</i>",
            "SL     : <i>obligation manquante \u2014 Fib 0 non d\u00e9rivable, lis sur ton chart</i>",
            "Risque : " + str(int(risk_usd)) + " $ \u2014 dimensionne \u00e0 la main",
            "\U0001F4C8 <a href='" + esc(get_tv_link(parsed.get("asset") or "", group)) + "'>Ouvrir le chart</a>"])

    stop = abs(entry - sl)
    unit = abs(target - entry) / 0.618

    def _ext(mult):
        d = (mult - 1.0) * unit
        return round((entry + d) if long_bias else (entry - d), 2)

    cval = CONTRACT_VALUE.get(group, CONTRACT_DEFAULT)
    lots = round(risk_usd / (stop * cval), 2) if (stop > 0 and cval > 0) else 0.0
    verb = "LIMITE BUY" if long_bias else "LIMITE SELL"
    rr   = round(abs(target - entry) / stop, 2) if stop > 0 else 0.0
    bar  = "\u2501" * 20

    L = hdr + [
        bar,
        "\u25b8 <b>" + verb + " " + str(lots) + " lot @ " + str(entry) + "</b>",
        "   SL " + str(round(sl, 2)) + "  \u00b7  TP " + str(round(target, 2)),
        bar,
        "Sens   : " + dir_txt,
        "Entr\u00e9e : <b>" + str(entry) + "</b> <i>(Fib 1 \u2014 pose la limite ici)</i>",
        "SL     : <b>" + str(round(sl, 2)) + "</b> <i>(Fib " + ("%g" % slf) + ", d\u00e9riv\u00e9)</i>",
        "TP1 <b>" + str(round(target, 2)) + "</b> \u00b7 TP2 " + str(_ext(2.618))
        + " \u00b7 TP3 " + str(_ext(3.618)) + " \u00b7 TP4 " + str(_ext(4.618)),
        bar,
        "Risque " + str(int(risk_usd)) + " $  \u00b7  Stop " + str(round(stop, 2))
        + " pts  \u00b7  R:R 1:" + str(rr) + " (TP1)",
        "Taille <b>" + str(lots) + " lots</b> <i>(specs " + group + " \u2014 \u00c0 V\u00c9RIFIER)</i>",
        bar,
        "\u23f3 <i>Pose l'ordre et pars : il se d\u00e9clenche seul si le prix revient sur le Fib 1. Sinon pas de trade (un setup qui file sans retest est manqu\u00e9).</i>",
        "\U0001F4C8 <a href='" + esc(get_tv_link(parsed.get("asset") or "", group)) + "'>Ouvrir le chart TradingView</a>",
        "\u26a0\ufe0f <i>D\u00e9mo. V\u00e9rifie la taille (specs broker) avant de poser.</i>"]
    return "\n".join(L)


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
    # v2.7.14 : payload brut complet en repr (une seule ligne de log Railway,
    # les \n multi-lignes ne sont plus éclatés) — indispensable au debug.
    print(("[WEBHOOK] RAW : " + repr(raw))[:500])
    # v2.7.15 : tracer l'?asset= reçu (jamais le token) — diagnostic des
    # alertes dont l'URL porte un mauvais actif.
    print(f"[WEBHOOK] URL asset={request.args.get('asset')!r}")
    if not raw:
        return jsonify({"error": "empty body"}), 400

    # Aiguillage : message hold (multi-lignes) vs format standard.
    # v2.7.14 : 'hold' cherché sur les 2 premières lignes (une ligne
    # 'Ticker: XXX' peut désormais précéder le type).
    asset_url = request.args.get("asset")
    head = "\n".join(raw.split("\n")[:2]).lower()
    if "hold" in head:
        parsed = parse_hold_message(raw, asset_hint=asset_url)
        if parsed is None:
            parsed = parse_fiblab_message(raw)
    else:
        parsed = parse_fiblab_message(raw)
    # Filet de sécurité : asset depuis l'URL si absent du message
    if not parsed.get("asset") and asset_url:
        parsed["asset"] = asset_url.upper()

    scoring = compute_score(parsed, history=alert_history)
    group   = get_asset_group(parsed.get("asset") or "")

    # v2.7.14 : garde-fou cohérence prix↔actif (flag, jamais de correction)
    coh = asset_coherence_warning(parsed, group)
    if coh:
        parsed["_coherence_warn"] = coh
        print(f"[COHERENCE] \u26a0\ufe0f {coh} | asset={parsed.get('asset')} raw={raw[:80]!r}")

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
        if user_id == TELEGRAM_CHAT_ID_2 and scoring["level"] != "PRIORITAIRE":
            continue
        if (user_id == TELEGRAM_CHAT_ID and TICKET_ENABLED
                and any(t in (parsed.get("type") or "").lower() for t in TICKET_TYPES)
                and _ticket_tf_ok(parsed.get("timeframe"))):
            results[user_id] = "-> ticket"
            continue
        notify, reason = should_notify(parsed, scoring, profile)
        if not notify:
            results[user_id] = f"filtré: {reason}"
            continue
        tg_msg = format_telegram_message(parsed, scoring, profile)
        sent   = send_telegram(tg_msg, user_id)
        results[user_id] = "✅" if sent else "❌"

    if TICKET_ENABLED and not robot_state["paused"]:
        try:
            ticket = build_trade_ticket(parsed, group)
            if ticket:
                send_telegram(ticket, TELEGRAM_CHAT_ID)
                results["ticket"] = "sent"
        except Exception as e:
            print(f"[TICKET] {e}")

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
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    n = evaluate_pending_outcomes()
    with db() as conn:
        remaining = conn.execute("SELECT COUNT(*) AS n FROM outcomes WHERE status='pending'").fetchone()["n"]
    return jsonify({"evaluated": n, "remaining_pending": remaining})


@app.route("/reeval", methods=["GET", "POST"])
def reeval_route():
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


@app.route("/rescore", methods=["GET", "POST"])
def rescore_route():
    """Recalcule le score ET le niveau de TOUTES les alertes stockées avec le
    scoring courant (poids Syn + bonus). Le bonus de CONFLUENCE est reconstruit
    fidèlement : on rejoue les alertes par ordre d'arrivée (id) et chaque alerte
    n'est scorée que contre celles qui l'ont précédée — comme en live.
    Ne touche PAS aux issues (win/loss) ; pour ça, voir /reeval."""
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    with db() as conn:
        rows = conn.execute(
            "SELECT id, asset, timeframe, type, side, price, scope, score, level "
            "FROM alerts ORDER BY id ASC"
        ).fetchall()
    hist = deque(maxlen=200)          # même capacité que l'historique live
    rescored = changed = 0
    with db() as conn:
        for r in rows:
            parsed = {"type": r["type"], "asset": r["asset"], "timeframe": r["timeframe"],
                      "side": r["side"], "price": r["price"], "scope": r["scope"]}
            sc = compute_score(parsed, history=hist)
            hist.appendleft({"asset": r["asset"], "side": r["side"],
                             "price": r["price"], "timeframe": r["timeframe"]})
            if sc["score"] != r["score"] or sc["level"] != r["level"]:
                changed += 1
            conn.execute("UPDATE alerts SET score=?, level=? WHERE id=?",
                         (sc["score"], sc["level"], r["id"]))
            rescored += 1
        conn.commit()
    return jsonify({"rescored": rescored, "changed": changed})


@app.route("/price_test", methods=["GET"])
def price_test():
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=48)
    bars = fetch_prices("xau", "XAUUSD", start, end)
    src = "twelvedata" if TWELVEDATA_API_KEY else "yahoo"
    sample = [{"t": b[0].isoformat(), "high": b[1], "low": b[2]} for b in bars[:3]]
    return jsonify({"source": src, "bars": len(bars), "sample": sample})


# ─────────────────────────────────────────────
# TABLEAU DE BORD DE CALIBRATION (rendu serveur, sans JS ni CDN)
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
.actions{float:right;display:flex;gap:8px}
.btn{font-size:.75rem;color:var(--blue);text-decoration:none;background:transparent;border:1px solid var(--bd);padding:5px 10px;border-radius:6px;cursor:pointer;font-family:inherit}
.btn:hover{border-color:var(--blue)}
.btn.active{border-color:var(--blue);color:var(--gold);font-weight:700}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 18px}
.chip{font-size:.72rem;color:var(--dim);text-decoration:none;border:1px solid var(--bd);padding:4px 12px;border-radius:20px}
.chip:hover{color:var(--blue);border-color:var(--blue)}
.chip.active{background:var(--blue);color:#04121f;border-color:var(--blue);font-weight:700}
@media print{.actions{display:none}*{-webkit-print-color-adjust:exact !important;print-color-adjust:exact !important}}
</style>"""


def _bar_rows(rows, color, nodata="aucune donn\u00e9e"):
    if not rows:
        return '<div class="muted">' + nodata + '</div>'
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


DASH_STR = {
    "fr": {
        "title": "\U0001F3AF Calibration du scoring",
        "sub": "Win rate & espérance des alertes par score / type / timeframe — pour ajuster les poids sur des faits",
        "pdf": "\U0001F5A8 Imprimer / PDF", "refresh": "\u21bb Rafraîchir",
        "evaluated": "Évaluées", "gwr": "Win rate global", "pending": "En attente", "flt_all": "Tout",
        "rmean_card": "R moyen (espérance)", "rtotal_card": "R total",
        "by_score": "Win rate par SCORE — le graphe clé",
        "by_type": "Win rate par TYPE", "by_tf": "Win rate par TIMEFRAME",
        "detail": "Détail par score", "nodata": "aucune donnée",
        "by_asset": "Win rate & espérance par ACTIF",
        "th_asset": "Actif", "asset_note": "Filtre par actif via les puces ci-dessus. Attention : les lignes antérieures au 10/07 peuvent porter un actif erroné (bug ?asset= corrigé en v2.7.14) — les vues par actif se fiabilisent avec les données récentes.",
        "exp_title": "Espérance par type (R) — la vraie mesure",
        "th_type": "Type", "th_rmean": "R moyen", "th_rtotal": "R total",
        "rnote": "<b>R moyen = espérance par trade.</b> Positif = profitable, négatif = perdant — quel que soit le win rate. C'est CE chiffre qui compte, pas le %. Rappel : la cible d'obligation des Hold est un objectif minimum, donc un R modeste est normal. Trié par espérance décroissante.",
        "note": "<b>Comment lire :</b> si ton scoring est bon, le win rate doit <b>monter avec le score</b> (un 12 gagne plus qu'un 7). Si une barre de score faible dépasse celle d'un score fort, les <b>poids sont à recalibrer</b>. Barres pâles = moins de 5 trades (peu fiable).",
        "empty": "Aucune alerte évaluée pour l'instant.<br><br>Les alertes sont notées automatiquement une fois passées 12h ({p} en attente).<br>Vérifie aussi que le cron <code>/evaluate</code> tourne sans erreur.",
    },
    "en": {
        "title": "\U0001F3AF Scoring calibration",
        "sub": "Alert win rate & expectancy by score / type / timeframe — to tune the weights on facts",
        "pdf": "\U0001F5A8 Print / PDF", "refresh": "\u21bb Refresh",
        "evaluated": "Evaluated", "gwr": "Overall win rate", "pending": "Pending", "flt_all": "All",
        "rmean_card": "Mean R (expectancy)", "rtotal_card": "Total R",
        "by_score": "Win rate by SCORE — the key chart",
        "by_type": "Win rate by TYPE", "by_tf": "Win rate by TIMEFRAME",
        "detail": "Detail by score", "nodata": "no data",
        "by_asset": "Win rate & expectancy by ASSET",
        "th_asset": "Asset", "asset_note": "Filter by asset via the chips above. Note: rows before Jul 10 may carry a wrong asset (?asset= bug fixed in v2.7.14) — per-asset views become reliable with recent data.",
        "exp_title": "Expectancy by type (R) — the real measure",
        "th_type": "Type", "th_rmean": "Mean R", "th_rtotal": "Total R",
        "rnote": "<b>Mean R = expectancy per trade.</b> Positive = profitable, negative = losing — regardless of win rate. This is the number that matters, not the %. Note: the Hold obligation target is a minimum objective, so a modest R is expected. Sorted by expectancy, descending.",
        "note": "<b>How to read:</b> if your scoring is good, win rate should <b>rise with the score</b> (a 12 wins more than a 7). If a low-score bar beats a high-score one, the <b>weights need recalibrating</b>. Pale bars = fewer than 5 trades (unreliable).",
        "empty": "No alert evaluated yet.<br><br>Alerts are scored automatically once they are 12h old ({p} pending).<br>Also check that the <code>/evaluate</code> cron runs without error.",
    },
}


@app.route("/stats_view", methods=["GET"])
def stats_view():
    if not check_secret():
        return ("unauthorized", 403)
    lang = (request.args.get("lang") or "fr").lower()
    if lang not in ("fr", "en"):
        lang = "fr"
    T = DASH_STR[lang]
    type_filter  = (request.args.get("type") or "").lower().strip()
    asset_filter = (request.args.get("asset") or "").lower().strip()   # groupe : xau/dax/solana/...
    from urllib.parse import quote
    with db() as conn:
        rows = conn.execute(
            "SELECT a.score, a.type, a.timeframe, a.grp, o.status, o.r_realized "
            "FROM alerts a JOIN outcomes o ON a.id = o.alert_id"
        ).fetchall()

    counts = {"win": 0, "loss": 0, "invalid": 0, "pending": 0, "skip": 0}
    by_score, by_type, by_tf = {}, {}, {}
    r_by_type = {}
    by_asset = {}          # v2.7.16 : agrégat par actif (toujours global, hors filtre asset)
    r_sum_all, r_cnt_all = 0.0, 0
    for r in rows:
        if type_filter and type_filter not in (r["type"] or "").lower():
            continue
        # tableau par actif : sur le périmètre du filtre TYPE uniquement
        _g = (r["grp"] or "?")
        _st0 = r["status"] or "pending"
        if _st0 in ("win", "loss"):
            d = by_asset.setdefault(_g, {"win": 0, "loss": 0, "rsum": 0.0, "rcnt": 0})
            d[_st0] += 1
            if r["r_realized"] is not None:
                d["rsum"] += r["r_realized"]
                d["rcnt"] += 1
        if asset_filter and _g.lower() != asset_filter:
            continue
        st = r["status"] or "pending"
        counts[st] = counts.get(st, 0) + 1
        if st in ("win", "loss"):
            by_score.setdefault(r["score"], {"win": 0, "loss": 0})[st] += 1
            by_type.setdefault(r["type"] or "?", {"win": 0, "loss": 0})[st] += 1
            by_tf.setdefault(r["timeframe"] or "?", {"win": 0, "loss": 0})[st] += 1
            rr = r["r_realized"]
            if rr is not None:
                d = r_by_type.setdefault(r["type"] or "?", {"sum": 0.0, "cnt": 0})
                d["sum"] += rr
                d["cnt"] += 1
                r_sum_all += rr
                r_cnt_all += 1

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
    mean_r_all = (r_sum_all / r_cnt_all) if r_cnt_all else 0.0

    def sgn(x):
        return ("+" if x > 0 else "") + str(x)

    fr_cls = "btn active" if lang == "fr" else "btn"
    en_cls = "btn active" if lang == "en" else "btn"

    def mkurl2(l, t, a=None):
        a = asset_filter if a is None else a
        u = "/stats_view?lang=" + l
        if t:
            u += "&type=" + quote(t)
        if a:
            u += "&asset=" + quote(a)
        return u
    head = ('<!DOCTYPE html><html lang="' + lang + '"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>FibLab — Calibration</title>' + DASH_CSS + '</head><body>')
    header = ('<div class="actions">'
              '<a class="btn" href="/export.csv">\u2b07 CSV</a>'
              '<button class="btn" onclick="window.print()">' + T["pdf"] + '</button>'
              '<a class="' + fr_cls + '" href="' + mkurl2("fr", type_filter) + '">FR</a>'
              '<a class="' + en_cls + '" href="' + mkurl2("en", type_filter) + '">EN</a>'
              '<a class="btn" href="' + mkurl2(lang, type_filter) + '">' + T["refresh"] + '</a>'
              '</div>'
              '<h1>' + T["title"] + '</h1>'
              '<div class="sub">' + T["sub"] + '</div>')

    _chip_defs = [("", T["flt_all"]), ("hold", "Hold"), ("bsut", "BSUT"),
                  ("first touch", "First Touch"), ("proximity", "Proximity")]
    chips = '<div class="chips">' + "".join(
        '<a class="chip' + (" active" if type_filter == kw else "") + '" href="'
        + mkurl2(lang, kw) + '">' + esc(lbl) + '</a>' for kw, lbl in _chip_defs) + '</div>'

    if tot_eval == 0:
        body = chips + '<div class="empty">' + T["empty"].format(p=counts["pending"]) + '</div>'
        return head + header + body + '</body></html>'

    wrc = "var(--grn)" if wr >= 50 else "var(--gold)"
    rc_all = "var(--grn)" if mean_r_all > 0 else "var(--red)"
    cards = ('<div class="grid">'
             + '<div class="stat"><div class="lbl">' + T["evaluated"] + '</div><div class="val" style="color:var(--blue)">' + str(tot_eval) + '</div></div>'
             + '<div class="stat"><div class="lbl">' + T["gwr"] + '</div><div class="val" style="color:' + wrc + '">' + str(wr) + '%</div></div>'
             + '<div class="stat"><div class="lbl">' + T["rmean_card"] + '</div><div class="val" style="color:' + rc_all + '">' + sgn(round(mean_r_all, 2)) + 'R</div></div>'
             + '<div class="stat"><div class="lbl">' + T["rtotal_card"] + '</div><div class="val" style="color:' + rc_all + '">' + sgn(round(r_sum_all, 1)) + 'R</div></div>'
             + '<div class="stat"><div class="lbl">Win</div><div class="val" style="color:var(--grn)">' + str(counts["win"]) + '</div></div>'
             + '<div class="stat"><div class="lbl">Loss</div><div class="val" style="color:var(--red)">' + str(counts["loss"]) + '</div></div>'
             + '<div class="stat"><div class="lbl">Invalid</div><div class="val" style="color:var(--dim)">' + str(counts["invalid"]) + '</div></div>'
             + '<div class="stat"><div class="lbl">' + T["pending"] + '</div><div class="val" style="color:var(--dim)">' + str(counts["pending"]) + '</div></div>'
             + '</div>')
    note = '<div class="note">' + T["note"] + '</div>'
    trows = []
    for r in bs:
        c = "var(--grn)" if r["wr"] >= 50 else "var(--gold)"
        trows.append('<tr><td>' + esc(r["k"]) + '</td><td style="color:var(--grn)">' + str(r["win"])
                     + '</td><td style="color:var(--red)">' + str(r["loss"]) + '</td><td>' + str(r["n"])
                     + '</td><td style="font-weight:700;color:' + c + '">' + str(r["wr"]) + '%</td></tr>')
    table = ('<div class="card"><h2>' + T["detail"] + '</h2><table><thead><tr>'
             '<th>Score</th><th>Win</th><th>Loss</th><th>N</th><th>Win rate</th></tr></thead><tbody>'
             + "".join(trows) + '</tbody></table></div>')

    exp_items = []
    for k, v in by_type.items():
        n = v["win"] + v["loss"]
        rd = r_by_type.get(k, {"sum": 0.0, "cnt": 0})
        mean_r = (rd["sum"] / rd["cnt"]) if rd["cnt"] else 0.0
        exp_items.append({"k": str(k), "n": n,
                          "wr": round(100 * v["win"] / n, 1) if n else 0,
                          "rmean": round(mean_r, 2), "rtotal": round(rd["sum"], 1)})
    exp_items.sort(key=lambda x: x["rmean"], reverse=True)
    exp_rows = []
    for it in exp_items:
        rc = "var(--grn)" if it["rmean"] > 0 else "var(--red)"
        exp_rows.append('<tr><td>' + esc(it["k"]) + '</td><td>' + str(it["n"])
                        + '</td><td>' + str(it["wr"]) + '%</td>'
                        + '<td style="font-weight:700;color:' + rc + '">' + sgn(it["rmean"])
                        + '</td><td style="color:' + rc + '">' + sgn(it["rtotal"]) + '</td></tr>')
    exp_table = ('<div class="card"><h2>' + T["exp_title"] + '</h2>'
                 + '<div class="note">' + T["rnote"] + '</div>'
                 + '<table><thead><tr><th>' + T["th_type"] + '</th><th>N</th><th>Win rate</th>'
                 + '<th>' + T["th_rmean"] + '</th><th>' + T["th_rtotal"] + '</th></tr></thead><tbody>'
                 + "".join(exp_rows) + '</tbody></table></div>')

    # v2.7.16 : tableau par actif (win rate + espérance)
    a_items = []
    for g, v in by_asset.items():
        n = v["win"] + v["loss"]
        mean_r = (v["rsum"] / v["rcnt"]) if v["rcnt"] else 0.0
        lbl = ASSET_META.get(g, {}).get("emoji", "") + " " + ASSET_META.get(g, {}).get("label", g)
        a_items.append({"g": g, "lbl": lbl.strip(), "n": n,
                        "wr": round(100 * v["win"] / n, 1) if n else 0,
                        "rmean": round(mean_r, 2), "rtotal": round(v["rsum"], 1)})
    a_items.sort(key=lambda x: x["rmean"], reverse=True)
    a_rows = []
    for it in a_items:
        rc = "var(--grn)" if it["rmean"] > 0 else "var(--red)"
        a_rows.append('<tr><td><a style="color:inherit" href="' + mkurl2(lang, type_filter, it["g"]) + '">'
                      + esc(it["lbl"]) + '</a></td><td>' + str(it["n"])
                      + '</td><td>' + str(it["wr"]) + '%</td>'
                      + '<td style="font-weight:700;color:' + rc + '">' + sgn(it["rmean"])
                      + '</td><td style="color:' + rc + '">' + sgn(it["rtotal"]) + '</td></tr>')
    asset_table = ('<div class="card"><h2>' + T["by_asset"] + '</h2>'
                   + '<div class="note">' + T["asset_note"] + '</div>'
                   + '<table><thead><tr><th>' + T["th_asset"] + '</th><th>N</th><th>Win rate</th>'
                   + '<th>' + T["th_rmean"] + '</th><th>' + T["th_rtotal"] + '</th></tr></thead><tbody>'
                   + "".join(a_rows) + '</tbody></table></div>') if a_items else ""

    body = (chips + cards
            + '<div class="card"><h2>' + T["by_score"] + '</h2>' + _bar_rows(bs, "#f5a623", T["nodata"]) + '</div>'
            + note
            + '<div class="card"><h2>' + T["by_type"] + '</h2>' + _bar_rows(bt, "#58a6ff", T["nodata"]) + '</div>'
            + exp_table
            + asset_table
            + '<div class="card"><h2>' + T["by_tf"] + '</h2>' + _bar_rows(btf, "#a78bfa", T["nodata"]) + '</div>'
            + table)
    return head + header + body + '</body></html>'


@app.route("/sl_sweep", methods=["GET"])
def sl_sweep():
    """Backtest : pour les Origin Hold ACTIVATED, rejoue le prix à travers
    plusieurs niveaux de stop (fractions Fibo, de serré à au-delà du Fib 0) et
    donne par niveau : % de stop touché, R:R, espérance. À lancer UNE fois à
    froid (refait les fetches -> ne pas boucler, sinon rate-limit)."""
    if not check_secret():
        return ("unauthorized", 403)
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(hours=EVAL_MIN_AGE_H)).isoformat()
    with db() as conn:
        rows = conn.execute(
            "SELECT a.id, a.ts, a.asset, a.grp, a.side, a.price, a.timeframe, a.target "
            "FROM alerts a JOIN outcomes o ON a.id = o.alert_id "
            "WHERE a.price IS NOT NULL AND a.side IS NOT NULL AND a.target IS NOT NULL "
            "AND a.ts <= ? AND LOWER(a.type) LIKE '%origin hold activated%' "
            "ORDER BY a.id DESC LIMIT 500",
            (cutoff,)
        ).fetchall()
    groups, order = {}, []
    for r in rows:
        try:
            ts = datetime.fromisoformat(r["ts"])
        except Exception:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if (now - ts).total_seconds() / 3600 < EVAL_MIN_AGE_H:
            continue
        if r["grp"] not in EVAL_RISK:
            continue
        key = (r["grp"], r["asset"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append((r, ts))

    agg = {f: {"win": 0, "loss": 0, "invalid": 0, "sum_r": 0.0} for f in STOP_FIB_LEVELS}
    n_used = 0
    _start = time.monotonic()
    for key in order:
        if time.monotonic() - _start > 45:
            break
        grp, asset = key
        items = groups[key]
        earliest = min(ts for _, ts in items)
        floor_dt = now - timedelta(hours=EVAL_LOOKBACK_MAX_H + EVAL_HORIZON_MAX_H)
        bars = fetch_prices(grp, asset, max(earliest - timedelta(hours=2), floor_dt), now)
        if not bars:
            continue
        for r, ts in items:
            entry, target = r["price"], r["target"]
            long_bias = (r["side"] == "Support")
            unit = abs(target - entry) / 0.618
            if unit <= 0:
                continue
            tf_h = tf_hours(r["timeframe"])
            horizon_h = min(max(EVAL_HORIZON_BARS * tf_h, EVAL_HORIZON_MIN_H), EVAL_HORIZON_MAX_H)
            end_win = min(ts + timedelta(hours=horizon_h), now)
            post = [b for b in bars if ts < b[0] <= end_win]
            if not post:
                continue
            tdist = abs(target - entry)
            elapsed = now >= ts + timedelta(hours=horizon_h)
            counted = False
            for f in STOP_FIB_LEVELS:
                sdist = (1.0 - f) * unit
                if sdist <= 0:
                    continue
                status = None
                for (_dt, hi, lo, _c) in post:
                    fav = (hi - entry) if long_bias else (entry - lo)
                    adv = (entry - lo) if long_bias else (hi - entry)
                    if adv >= sdist:
                        status = "loss"
                        break
                    if fav >= tdist:
                        status = "win"
                        break
                if status is None:
                    if elapsed:
                        status = "invalid"
                    else:
                        continue
                agg[f][status] += 1
                if status == "win":
                    agg[f]["sum_r"] += tdist / sdist
                elif status == "loss":
                    agg[f]["sum_r"] += -1.0
                counted = True
            if counted:
                n_used += 1

    def _lbl(f):
        if f == 0.0:
            return "Fib 0 (actuel)"
        if f == -1.0:
            return "Fib -1 (large)"
        return "Fib " + ("%g" % f)

    rowdata, best_f, best_e = [], None, None
    for f in STOP_FIB_LEVELS:
        a = agg[f]
        dec = a["win"] + a["loss"]
        wr = round(100 * a["win"] / dec, 1) if dec else 0.0
        stop_pct = round(100 * a["loss"] / dec, 1) if dec else 0.0
        exp = round(a["sum_r"] / dec, 3) if dec else 0.0
        rr = round(0.618 / (1.0 - f), 2) if (1.0 - f) != 0 else 0.0
        rowdata.append((f, rr, dec, wr, stop_pct, exp))
        if dec and (best_e is None or exp > best_e):
            best_e, best_f = exp, f

    trows = ""
    for f, rr, dec, wr, stop_pct, exp in rowdata:
        ec = "var(--grn)" if exp > 0 else "var(--red)"
        hl = " style=\"background:#132a1e\"" if f == best_f else ""
        trows += ("<tr" + hl + "><td>" + _lbl(f) + "</td><td>1:" + str(rr) + "</td><td>"
                  + str(dec) + "</td><td>" + str(wr) + "%</td><td>" + str(stop_pct) + "%</td>"
                  + "<td style=\"font-weight:700;color:" + ec + "\">"
                  + (("+" if exp > 0 else "") + str(exp)) + "R</td></tr>")

    head = ('<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>FibLab \u2014 SL Sweep</title>' + DASH_CSS + '</head><body>')
    body = ("<h1>\U0001F3AF Sweep de Stop Loss</h1>"
            "<div class=\"sub\">Origin Hold ACTIVATED \u2014 " + str(n_used) + " trades. "
            "Sortie mesur\u00e9e \u00e0 TP1 (1.618). Stop serr\u00e9 = meilleur R:R mais plus de stop-outs.</div>"
            "<div class=\"card\"><table><thead><tr><th>Stop</th><th>R:R</th><th>N</th>"
            "<th>Win rate</th><th>% stop touch\u00e9</th><th>Esp\u00e9rance</th></tr></thead><tbody>"
            + trows + "</tbody></table></div>"
            "<div class=\"note\">Ligne verte = meilleure esp\u00e9rance. <b>% stop touch\u00e9</b> = "
            "ton indicateur cl\u00e9. L'esp\u00e9rance int\u00e8gre le R:R (un stop serr\u00e9 peut "
            "gagner malgr\u00e9 plus de sorties). Mesur\u00e9 \u00e0 TP1 seulement ; les runners "
            "TP2+ ajoutent par-dessus. \u00c9chantillon modeste \u2192 \u00e0 revalider en d\u00e9mo.</div>")
    return head + body + "</body></html>"


@app.route("/db_count", methods=["GET"])
def db_count():
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    with db() as conn:
        a = conn.execute("SELECT COUNT(*) AS n FROM alerts").fetchone()["n"]
        o = conn.execute("SELECT COUNT(*) AS n FROM outcomes").fetchone()["n"]
        p = conn.execute("SELECT COUNT(*) AS n FROM profiles").fetchone()["n"]
    return jsonify({"alerts": a, "outcomes": o, "profiles": p, "db_path": DB_PATH})


@app.route("/export.csv", methods=["GET"])
def export_csv():
    """Dump CSV complet : chaque alerte + son issue (statut, MFE/MAE, R réalisé,
    note). Pour analyse tableur / partage aux collaborateurs. Content-Disposition
    en attachment → le navigateur télécharge le fichier."""
    if not check_secret():
        return ("unauthorized", 403)
    import csv, io
    from flask import Response
    with db() as conn:
        rows = conn.execute(
            "SELECT a.id, a.ts, a.asset, a.grp, a.timeframe, a.type, a.side, a.price, "
            "a.scope, a.score, a.level, a.target, a.move_pct, "
            "o.status, o.mfe_pts, o.mae_pts, o.r_realized, o.note "
            "FROM alerts a LEFT JOIN outcomes o ON a.id = o.alert_id "
            "ORDER BY a.id"
        ).fetchall()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "ts", "asset", "group", "timeframe", "type", "side", "price",
                "scope", "score", "level", "target", "move_pct", "status", "mfe_pts",
                "mae_pts", "r_realized", "note"])
    for r in rows:
        w.writerow([r["id"], r["ts"], r["asset"], r["grp"], r["timeframe"], r["type"],
                    r["side"], r["price"], r["scope"], r["score"], r["level"], r["target"],
                    r["move_pct"], r["status"], r["mfe_pts"], r["mae_pts"], r["r_realized"],
                    r["note"]])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="fiblab_export.csv"'})


@app.route("/status", methods=["GET"])
def status():
    profiles_summary = {uid: {"mode": p["mode"], "paused": p["paused"]}
                        for uid, p in user_profiles.items()}
    return jsonify({
        "status": "killswitch" if robot_state["paused"] else "running",
        "version": "2.7.16",
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


@app.route("/hype", methods=["GET"])
def dashboard_hype():
    return render_template("dashboard.html", alerts=list(histories["hype"]), page="hype",
                           counts={g: len(h) for g, h in histories.items()})


@app.route("/sui", methods=["GET"])
def dashboard_sui():
    return render_template("dashboard.html", alerts=list(histories["sui"]), page="sui",
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
    scoring = compute_score(parsed, history=alert_history)
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


@app.route("/test_hold", methods=["GET"])
def test_hold():
    """Test du parser hold : simule un message ACTIVATED avec cible d'obligation."""
    raw = ("Hold ACTIVATED\nTF: 1440\nSupport\nWick Engulfment\n"
           "Entry touched: 4310.00\nExit: 4355.00\nMove%: 1.04")
    parsed  = parse_hold_message(raw, asset_hint="XAUUSD")
    scoring = compute_score(parsed, history=alert_history)
    group   = get_asset_group(parsed.get("asset") or "")
    try:
        save_alert(parsed, scoring, group)
    except Exception as e:
        print(f"[DB] _test_hold save_alert : {e}")
    msg = format_telegram_message(parsed, scoring, get_profile(TELEGRAM_CHAT_ID))
    sent = send_telegram(msg, TELEGRAM_CHAT_ID)
    return jsonify({"telegram_charlie": sent, "parsed": parsed, "scoring": scoring})


# ─────────────────────────────────────────────
# INIT (au chargement du module → fonctionne aussi sous gunicorn)
# ─────────────────────────────────────────────
init_db()
migrate_db()                     # v2.6.0 : ajoute colonnes target/move_pct si besoin
clean_seed_rows()
load_profiles()
load_alert_history()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
