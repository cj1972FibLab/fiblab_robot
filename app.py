"""
╔══════════════════════════════════════════════════════════════╗
║         FIBLAB ROBOT — Webhook Trading Server  (v2.7.22)     ║
║         Charlie Joe 1972 — Juillet 2026                      ║
║                                                              ║
║  Patch v2.7.22 "Précision des tickets" :                     ║
║   • SL/TP/stop arrondis selon la magnitude du prix :         ║
║     ≥1000→2 déc. · ≥100→3 · ≥1→4 · <1→6                      ║
║                                                              ║
║  Patch v2.7.21 "Journal de trading" :                        ║
║   • /journal : comptes (UFunded 360k / DD 16k absolu,        ║
║     Jupiter, Phantom), solde manuel, marge avant violation   ║
║     DD avec barre de danger, trades pré-remplis depuis les   ║
║     alertes ticketables, sorties partielles par palier,      ║
║     champ déviation, R géométrique + P&L indicatif           ║
║   • /balance <compte> <solde> et /journal sur Telegram       ║
║                                                              ║
║  Patch v2.7.20 "Stop paramétrable PAR ACTIF" :               ║
║   • /sl_fib <groupe> <fraction> : surcharge le stop d'un     ║
║     actif (éval + ticket + tp_ladder) ; off pour retirer ;   ║
║     les autres restent au global. Runtime (reset au deploy)  ║
║   • /sl_sweep?asset=<groupe> : sweep restreint à un actif —  ║
║     la SEULE base légitime pour choisir une surcharge        ║
║                                                              ║
║  Patch v2.7.19 "Notifications FR/EN par utilisateur" :       ║
║   • /lang fr|en : langue des alertes ET du ticket, par       ║
║     chat_id, persistée en base (survit aux redéploiements)   ║
║   • Avert. cohérence localisé ; détails de scoring encore    ║
║     FR (générés par compute_score — chantier séparé si       ║
║     besoin)                                                  ║
║                                                              ║
║  Patch v2.7.18 "TP Ladder feedback" :                        ║
║   • /tp_ladder : % de trades atteignant TP1/2/3/4 avant le   ║
║     stop + espérance comparée de 3 plans de sortie (tout à   ║
║     TP1 / 25% fixes / 25% avec stop remonté = ton playbook)  ║
║                                                              ║
║  Patch v2.7.17 "Aide dashboard + nettoyage TF" :             ║
║   • Bloc "❓ Comment lire" repliable sur chaque module du     ║
║     dashboard (pièges ARMED/PROXIMITY, proxy vs réel, TF     ║
║     non mesurables, pollution par actif) — bilingue          ║
║   • /fix_tf : remap one-shot des TF pollués M1..M5/6/7 →     ║
║     1D..7D (Hold uniquement) + outcomes remis en pending     ║
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
from flask import Flask, request, jsonify, redirect, render_template
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
                lang      TEXT DEFAULT 'fr',
                tf_custom TEXT
            )
        """)
        try:  # v2.7.19 : migration lang sur base existante
            conn.execute("ALTER TABLE profiles ADD COLUMN lang TEXT DEFAULT 'fr'")
        except Exception:
            pass
        # v2.7.21 : JOURNAL DE TRADING
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT UNIQUE,
                kind     TEXT,              -- propfirm | crypto
                capital  REAL,              -- capital de référence
                dd_max   REAL,              -- drawdown max ABSOLU (NULL si aucun)
                balance  REAL,              -- solde courant, MIS À JOUR PAR L'UTILISATEUR
                active   INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                opened_ts  TEXT,
                closed_ts  TEXT,
                asset      TEXT,
                grp        TEXT,
                side       TEXT,             -- LONG | SHORT
                entry      REAL,
                sl_initial REAL,
                risk_usd   REAL,
                status     TEXT DEFAULT 'open',   -- open | closed | cancelled
                exits      TEXT DEFAULT '[]',     -- JSON [{ts,price,frac,label}]
                r_realized REAL,
                pnl_usd    REAL,
                setup      TEXT,             -- ex: Origin Hold ACTIVATED H4
                deviation  TEXT,             -- pourquoi j'ai dévié du ticket
                alert_id   INTEGER,          -- lien vers l'alerte source
                note       TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)
        # Seed des comptes au premier lancement (modifiable ensuite via /journal)
        if conn.execute("SELECT COUNT(*) AS n FROM accounts").fetchone()["n"] == 0:
            conn.executemany(
                "INSERT INTO accounts (name,kind,capital,dd_max,balance) VALUES (?,?,?,?,?)",
                [("UFunded", "propfirm", 360000.0, 16000.0, 360000.0),
                 ("Jupiter", "crypto", 0.0, None, 0.0),
                 ("Phantom", "crypto", 0.0, None, 0.0)])
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
                    "lang":      (row["lang"] if "lang" in row.keys() else None) or "fr",
                    "tf_custom": json.loads(row["tf_custom"] or "{}"),
                }
    except Exception as e:
        print(f"[DB] load_profiles : {e}")


def save_profile(chat_id: str, profile: dict):
    with db() as conn:
        conn.execute(
            "INSERT INTO profiles (chat_id,mode,paused,lang,tf_custom) VALUES (?,?,?,?,?) "
            "ON CONFLICT(chat_id) DO UPDATE SET "
            "mode=excluded.mode, paused=excluded.paused, lang=excluded.lang, "
            "tf_custom=excluded.tf_custom",
            (chat_id, profile["mode"], int(profile["paused"]),
             profile.get("lang", "fr"), json.dumps(profile["tf_custom"]))
        )
        conn.commit()


# ─────────────────────────────────────────────
# PROFILS UTILISATEURS — indépendants par chat_id
# ─────────────────────────────────────────────
def default_profile():
    return {
        "paused": False,
        "mode": "swing",
        "lang": "fr",
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
# v2.7.20 : surcharge PAR ACTIF (groupe -> fraction). Vide par défaut = tout le
# monde au global. Runtime (reset au redéploiement), comme /ideal et /ticket_tf.
robot_state["sl_fib_asset"] = {}


def sl_fib_for(group):
    """Fraction Fibo du stop pour un groupe : surcharge par actif si définie,
    sinon le réglage global /sl_fib."""
    ov = robot_state.get("sl_fib_asset", {})
    if group in ov:
        return ov[group]
    return robot_state.get("sl_fib", SL_FIB_DEFAULT)


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



# v2.7.19 — libellés des notifications/ticket Telegram, par langue de profil.
TG_STR = {
    "fr": {
        "alert": "ALERTE", "score": "Score", "asset": "Asset", "level": "Niveau",
        "type": "Type", "tf": "TF", "side": "Side", "scope": "Scope", "mode": "Mode",
        "scoring": "Scoring", "action": "Action", "watch": "\u2192 Surveille M1 maintenant",
        "setup_long": "\u2192 Setup <b>LONG</b> potentiel", "setup_short": "\u2192 Setup <b>SHORT</b> potentiel",
        "obligation": "\u2192 \U0001F3AF Cible obligation", "sl_generic": "\u2192 SL vis\u00e9 : 5-10 pts",
        "open_chart": "Ouvrir le chart", "see_chart": "voir chart",
        "coh": "prix {p} hors gamme {g} [{lo}\u2013{hi}] \u2014 actif probablement MAL \u00c9TIQUET\u00c9 (v\u00e9rifie ?asset=/Ticker)",
        "tk_title": "ORDRE LIMITE", "tk_demo": "d\u00e9mo", "tk_dir": "Sens", "tk_entry": "Entr\u00e9e",
        "tk_entry_note": "(Fib 1 \u2014 pose la limite ici)", "tk_sl_note": "(Fib {f}, d\u00e9riv\u00e9)",
        "tk_long": "\U0001F7E2 LONG (achat)", "tk_short": "\U0001F534 SHORT (vente)",
        "tk_risk": "Risque", "tk_stop": "Stop", "tk_size": "Taille",
        "tk_size_note": "(specs {g} \u2014 \u00c0 V\u00c9RIFIER)",
        "tk_missing": "obligation manquante \u2014 Fib 0 non d\u00e9rivable, lis sur ton chart",
        "tk_size_hand": "$ \u2014 dimensionne \u00e0 la main",
        "tk_park": "\u23f3 <i>Pose l'ordre et pars : il se d\u00e9clenche seul si le prix revient sur le Fib 1. Sinon pas de trade (un setup qui file sans retest est manqu\u00e9).</i>",
        "tk_chart": "Ouvrir le chart TradingView",
        "tk_demo_warn": "\u26a0\ufe0f <i>D\u00e9mo. V\u00e9rifie la taille (specs broker) avant de poser.</i>",
        "tk_no_order": "\u2014 NE PAS POSER sans v\u00e9rifier l'actif",
    },
    "en": {
        "alert": "ALERT", "score": "Score", "asset": "Asset", "level": "Level",
        "type": "Type", "tf": "TF", "side": "Side", "scope": "Scope", "mode": "Mode",
        "scoring": "Scoring", "action": "Action", "watch": "\u2192 Watch M1 now",
        "setup_long": "\u2192 Potential <b>LONG</b> setup", "setup_short": "\u2192 Potential <b>SHORT</b> setup",
        "obligation": "\u2192 \U0001F3AF Obligation target", "sl_generic": "\u2192 Target SL: 5-10 pts",
        "open_chart": "Open chart", "see_chart": "see chart",
        "coh": "price {p} outside {g} range [{lo}\u2013{hi}] \u2014 asset likely MISLABELED (check ?asset=/Ticker)",
        "tk_title": "LIMIT ORDER", "tk_demo": "demo", "tk_dir": "Dir.", "tk_entry": "Entry",
        "tk_entry_note": "(Fib 1 \u2014 park the limit here)", "tk_sl_note": "(Fib {f}, derived)",
        "tk_long": "\U0001F7E2 LONG (buy)", "tk_short": "\U0001F534 SHORT (sell)",
        "tk_risk": "Risk", "tk_stop": "Stop", "tk_size": "Size",
        "tk_size_note": "(specs {g} \u2014 VERIFY)",
        "tk_missing": "missing obligation \u2014 Fib 0 not derivable, read it on your chart",
        "tk_size_hand": "$ \u2014 size it by hand",
        "tk_park": "\u23f3 <i>Park the order and walk away: it fills by itself if price retests Fib 1. No retest, no trade (a setup that runs without retest is a missed one).</i>",
        "tk_chart": "Open the TradingView chart",
        "tk_demo_warn": "\u26a0\ufe0f <i>Demo. Verify the size (broker specs) before parking.</i>",
        "tk_no_order": "\u2014 DO NOT PARK before verifying the asset",
    },
}


def tg_lang(profile):
    return "en" if (profile or {}).get("lang") == "en" else "fr"


def format_telegram_message(parsed: dict, scoring: dict, profile: dict = None) -> str:
    asset   = parsed.get("asset") or None
    group   = get_asset_group(asset) if asset else None
    meta    = ASSET_META.get(group, {"emoji": "📡", "label": asset or "?"})
    is_atr  = "atr" in (parsed.get("type") or "").lower()
    tv_link = get_tv_link(asset, group)
    mode    = (profile or {}).get("mode", "swing")
    S       = TG_STR[tg_lang(profile)]   # v2.7.19

    side_emoji    = "🟢" if parsed.get("side") == "Support" else "🔴"
    scope_tag     = "✅ Pure" if parsed.get("scope") == "Pure" else "⬜ Non-Pure"
    asset_display = f"{meta['emoji']} {esc(asset)}" if asset else f"{meta['emoji']} {S['see_chart']}"

    # Ligne cible : si une cible d'obligation est fournie (Exit du hold ou Target),
    # on l'affiche à la place du SL générique.
    target   = parsed.get("target")
    move_pct = parsed.get("move_pct")
    if target:
        tgt_line = f"{S['obligation']} : <b>{esc(target)}</b>"
        if move_pct:
            tgt_line += f"  (<b>{esc(move_pct)}%</b>)"
    else:
        tgt_line = S["sl_generic"]

    setup = S["setup_long"] if parsed.get("side") == "Support" else S["setup_short"]
    action = f"{S['watch']}\n{setup}\n{tgt_line}"

    # v2.7.14 : avertissement de cohérence prix↔actif, bien visible
    coh_line = ""
    if parsed.get("_coherence_data"):
        p, g, lo, hi = parsed["_coherence_data"]
        coh_line = "\u26a0\ufe0f <b>" + esc(S["coh"].format(p=p, g=g.upper(), lo=lo, hi=hi)) + "</b>\n"
    elif parsed.get("_coherence_warn"):
        coh_line = f"\u26a0\ufe0f <b>{esc(parsed['_coherence_warn'])}</b>\n"

    msg = (
        f"{scoring['emoji']} <b>{S['alert']} {scoring['level']} — {S['score']} {scoring['score']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{coh_line}"
        f"{S['asset']:<8} : <b>{asset_display}</b>\n"
        f"{S['level']:<8} : <b>{esc(parsed.get('price', '?'))}</b>\n"
        f"{S['type']:<8} : {'📡 ' if is_atr else ''}{esc(parsed.get('type', '?'))}\n"
        f"{S['tf']:<8} : {esc(parsed.get('timeframe', '?'))}\n"
        f"{S['side']:<8} : {side_emoji} {esc(parsed.get('side', '?'))}\n"
        f"{S['scope']:<8} : {scope_tag}\n"
        f"{S['mode']:<8} : {esc(mode.upper())}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{S['scoring']} :\n"
    )
    for d in scoring["details"]:
        msg += f"  • {esc(d)}\n"

    tv_line = f"\n📈 <a href='{esc(tv_link)}'>{S['open_chart']}</a>" if tv_link else ""
    msg += (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{S['action']} :\n{action}\n"
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

    elif cmd == "/balance":
        # /balance ufunded 361200  — mise à jour rapide du solde d'un compte
        if chat_id != TELEGRAM_CHAT_ID:
            msg = "\u26d4 Commande réservée à l'admin."
        else:
            arg2 = parts[2] if len(parts) > 2 else ""
            try:
                val = float(arg2.replace(",", ".").replace(" ", ""))
            except (ValueError, AttributeError):
                val = None
            with db() as conn:
                accts = conn.execute("SELECT * FROM accounts WHERE active=1").fetchall()
                match = [a for a in accts if arg and a["name"].lower().startswith(arg)]
                if len(match) == 1 and val is not None:
                    a = match[0]
                    conn.execute("UPDATE accounts SET balance=? WHERE id=?", (val, a["id"]))
                    conn.commit()
                    extra = ""
                    if a["dd_max"]:
                        floor = (a["capital"] or 0) - a["dd_max"]
                        margin = val - floor
                        extra = (f"\nMarge avant violation DD : <b>{margin:,.0f} $</b>"
                                 f" (plancher {floor:,.0f} $)").replace(",", " ")
                        if margin < a["dd_max"] * 0.25:
                            extra += "\n\U0001F6A8 <b>ZONE ROUGE</b> — réduis le risque."
                    msg = f"\U0001F4B0 <b>{a['name']}</b> : solde \u2192 <b>{val:,.0f} $</b>".replace(",", " ") + extra
                else:
                    lines = [f"\u2022 {a['name']} : {(a['balance'] or 0):,.0f} $".replace(",", " ") for a in accts]
                    msg = "Soldes :\n" + "\n".join(lines) + "\n\nUsage : /balance ufunded 361200"

    elif cmd == "/journal":
        base = "https://acceptable-vision-production-a0df.up.railway.app/journal"
        msg = f"\U0001F4D2 <a href='{base}{('?token=' + WEBHOOK_SECRET) if WEBHOOK_SECRET else ''}'>Ouvrir le journal</a>"

    elif cmd == "/lang":
        if arg in ("fr", "en"):
            profile["lang"] = arg
            save_profile(chat_id, profile)
            msg = ("\U0001F1EB\U0001F1F7 Notifications en <b>fran\u00e7ais</b>." if arg == "fr"
                   else "\U0001F1EC\U0001F1E7 Notifications in <b>English</b>.")
        else:
            cur = profile.get("lang", "fr")
            msg = (f"Langue actuelle / current language : <b>{cur}</b>\n"
                   f"Usage : /lang fr | /lang en")

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
            # v2.7.20 : /sl_fib 0.5 (global) | /sl_fib xau 0 | /sl_fib xau off
            arg2 = parts[2] if len(parts) > 2 else ""
            grp_arg = arg if arg in ASSET_META else None

            def _pf(s):
                try:
                    return float(s.replace(",", "."))
                except (ValueError, AttributeError):
                    return None

            if grp_arg and arg2 == "off":
                robot_state.setdefault("sl_fib_asset", {}).pop(grp_arg, None)
                msg = (f"\U0001F3AF Surcharge <b>{grp_arg}</b> retirée \u2192 stop global "
                       f"Fib {robot_state.get('sl_fib', SL_FIB_DEFAULT):g}.\n(/reeval pour recalculer)")
            elif grp_arg:
                v = _pf(arg2)
                if v is not None and -2.0 <= v < 1.0:
                    robot_state.setdefault("sl_fib_asset", {})[grp_arg] = v
                    rr = round(0.618 / (1.0 - v), 2) if (1.0 - v) != 0 else 0.0
                    msg = (f"\U0001F3AF <b>{grp_arg} : stop = Fib {v:g}</b> (éval + ticket)\n"
                           f"R:R sur TP1 = 1:{rr} \u00b7 les autres actifs restent au global.\n"
                           f"\u26a0\ufe0f Justifie-le par /sl_sweep?asset={grp_arg} (n\u226530) — "
                           f"pas à l'intuition.\n(/reeval pour recalculer)")
                else:
                    msg = f"Usage : /sl_fib {grp_arg} 0.786 | 0.5 | 0 | -1 | off"
            else:
                v = _pf(arg)
                if v is not None and -2.0 <= v < 1.0:
                    robot_state["sl_fib"] = v
                    rr = round(0.618 / (1.0 - v), 2) if (1.0 - v) != 0 else 0.0
                    msg = (f"\U0001F3AF <b>Stop global = Fib {v:g}</b> (éval + ticket)\n"
                           f"R:R sur TP1 = 1:{rr}\n"
                           f"0 = Fib 0 large \u00b7 0.5 = mi-chemin \u00b7 0.786 = serré\n"
                           f"(fais /reeval pour recalculer le dashboard à ce stop)")
                else:
                    cur = robot_state.get("sl_fib", SL_FIB_DEFAULT)
                    ov = robot_state.get("sl_fib_asset", {})
                    ov_txt = ("\nSurcharges : " + ", ".join(f"{k}={v:g}" for k, v in ov.items())) if ov else ""
                    msg = (f"Stop global : <b>Fib {cur:g}</b>{ov_txt}\n"
                           f"Usage : /sl_fib 0.5 (global) \u00b7 /sl_fib xau 0.786 \u00b7 /sl_fib xau off")

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
                _slf = sl_fib_for(r["grp"])   # v2.7.20 : stop par actif
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
def build_trade_ticket(parsed, group, profile=None):
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
    S = TG_STR[tg_lang(profile)]   # v2.7.19
    risk_usd  = TICKET_CAPITAL * TICKET_RISK_PCT / 100.0
    slf = sl_fib_for(group)   # v2.7.20 : stop par actif
    sl = _stop_from_fib(entry, target, long_bias, slf)
    asset = esc(parsed.get("asset") or "?")
    tf    = esc(parsed.get("timeframe") or "?")
    typ   = esc(parsed.get("type") or "")
    dir_txt = S["tk_long"] if long_bias else S["tk_short"]
    hdr = ["\U0001F4CB <b>" + S["tk_title"] + "</b> \u2014 " + S["tk_demo"] + " " + str(int(TICKET_CAPITAL / 1000)) + "k",
           "<b>" + asset + "</b> \u00b7 TF " + tf + " \u00b7 " + typ]
    # v2.7.14 : cohérence prix↔actif — NE PAS poser cet ordre sans vérifier
    if parsed.get("_coherence_warn"):
        _cw = parsed["_coherence_warn"]
        if parsed.get("_coherence_data"):
            p, g, lo, hi = parsed["_coherence_data"]
            _cw = S["coh"].format(p=p, g=g.upper(), lo=lo, hi=hi)
        hdr.append("\u26a0\ufe0f <b>" + esc(_cw) + "</b> " + S["tk_no_order"])

    if sl is None or target is None:
        return "\n".join(hdr + [
            "\u2501" * 20,
            S["tk_dir"] + "   : " + dir_txt,
            S["tk_entry"] + " : <b>" + str(entry) + "</b> <i>(Fib 1)</i>",
            "SL     : <i>" + S["tk_missing"] + "</i>",
            S["tk_risk"] + " : " + str(int(risk_usd)) + " " + S["tk_size_hand"],
            "\U0001F4C8 <a href='" + esc(get_tv_link(parsed.get("asset") or "", group)) + "'>" + S["open_chart"] + "</a>"])

    stop = abs(entry - sl)
    unit = abs(target - entry) / 0.618

    # v2.7.22 : précision adaptée au prix (2 déc. n'a aucun sens sur SUI à 0.74)
    _dec = 2 if abs(entry) >= 1000 else (3 if abs(entry) >= 100 else (4 if abs(entry) >= 1 else 6))

    def _px(v):
        return round(v, _dec)

    def _ext(mult):
        d = (mult - 1.0) * unit
        return _px((entry + d) if long_bias else (entry - d))

    cval = CONTRACT_VALUE.get(group, CONTRACT_DEFAULT)
    lots = round(risk_usd / (stop * cval), 2) if (stop > 0 and cval > 0) else 0.0
    verb = "LIMITE BUY" if long_bias else "LIMITE SELL"
    rr   = round(abs(target - entry) / stop, 2) if stop > 0 else 0.0
    bar  = "\u2501" * 20

    L = hdr + [
        bar,
        "\u25b8 <b>" + verb + " " + str(lots) + " lot @ " + str(entry) + "</b>",
        "   SL " + str(_px(sl)) + "  \u00b7  TP " + str(_px(target)),
        bar,
        S["tk_dir"] + "   : " + dir_txt,
        S["tk_entry"] + " : <b>" + str(entry) + "</b> <i>" + S["tk_entry_note"] + "</i>",
        "SL     : <b>" + str(_px(sl)) + "</b> <i>" + S["tk_sl_note"].format(f=("%g" % slf)) + "</i>",
        "TP1 <b>" + str(_px(target)) + "</b> \u00b7 TP2 " + str(_ext(2.618))
        + " \u00b7 TP3 " + str(_ext(3.618)) + " \u00b7 TP4 " + str(_ext(4.618)),
        bar,
        S["tk_risk"] + " " + str(int(risk_usd)) + " $  \u00b7  " + S["tk_stop"] + " " + str(round(stop, _dec))
        + " pts  \u00b7  R:R 1:" + str(rr) + " (TP1)",
        S["tk_size"] + " <b>" + str(lots) + " lots</b> <i>" + S["tk_size_note"].format(g=group) + "</i>",
        bar,
        S["tk_park"],
        "\U0001F4C8 <a href='" + esc(get_tv_link(parsed.get("asset") or "", group)) + "'>" + S["tk_chart"] + "</a>",
        S["tk_demo_warn"]]
    return "\n".join(L)



# ─────────────────────────────────────────────
# JOURNAL DE TRADING (v2.7.21)
# ─────────────────────────────────────────────
def _tok():
    return ("?token=" + WEBHOOK_SECRET) if WEBHOOK_SECRET else ""


def _trade_r(t):
    """R réalisé (géométrique, broker-agnostique) + fraction encore ouverte.
    R d'une sortie = frac × (exit−entry)/(entry−sl), signé par le sens."""
    try:
        exits = json.loads(t["exits"] or "[]")
    except Exception:
        exits = []
    entry, sl = t["entry"], t["sl_initial"]
    if entry is None or sl is None or entry == sl:
        return 0.0, 1.0, exits
    risk_pts = abs(entry - sl)
    sign = 1.0 if (t["side"] or "").upper() == "LONG" else -1.0
    r = sum(e["frac"] * sign * (e["price"] - entry) / risk_pts for e in exits)
    open_frac = max(0.0, 1.0 - sum(e["frac"] for e in exits))
    return r, open_frac, exits


@app.route("/journal", methods=["GET"])
def journal_view():
    if not check_secret():
        return ("unauthorized", 403)
    tok = _tok()
    amp = "&" if tok else "?"
    prefill_id = request.args.get("prefill")
    with db() as conn:
        accts = conn.execute("SELECT * FROM accounts WHERE active=1 ORDER BY id").fetchall()
        open_tr = conn.execute(
            "SELECT t.*, a.name AS acct FROM trades t JOIN accounts a ON a.id=t.account_id "
            "WHERE t.status='open' ORDER BY t.opened_ts DESC").fetchall()
        closed_tr = conn.execute(
            "SELECT t.*, a.name AS acct FROM trades t JOIN accounts a ON a.id=t.account_id "
            "WHERE t.status!='open' ORDER BY t.closed_ts DESC LIMIT 30").fetchall()
        # Alertes ticketables récentes pour le pré-remplissage
        recents = conn.execute(
            "SELECT id, ts, asset, grp, timeframe, type, side, price, target FROM alerts "
            "WHERE LOWER(type) LIKE '%origin hold activated%' AND price IS NOT NULL "
            "AND target IS NOT NULL ORDER BY id DESC LIMIT 12").fetchall()

    # Valeurs de pré-remplissage depuis une alerte (mêmes maths que le ticket)
    pf = {"asset": "", "grp": "", "side": "LONG", "entry": "", "sl": "", "setup": "", "alert_id": ""}
    if prefill_id:
        with db() as conn:
            al = conn.execute("SELECT * FROM alerts WHERE id=?", (prefill_id,)).fetchone()
        if al:
            long_bias = (al["side"] == "Support")
            slf = sl_fib_for(al["grp"])
            slv = _stop_from_fib(al["price"], al["target"], long_bias, slf)
            pf = {"asset": al["asset"] or "", "grp": al["grp"] or "",
                  "side": "LONG" if long_bias else "SHORT",
                  "entry": al["price"], "sl": (round(slv, 4) if slv is not None else ""),
                  "setup": f"{al['type']} {al['timeframe'] or ''}".strip(),
                  "alert_id": al["id"]}

    def money(x):
        return f"{x:,.0f}".replace(",", " ")

    # ── Cartes comptes ──
    acct_cards = ""
    for a in accts:
        bal, cap = a["balance"] or 0.0, a["capital"] or 0.0
        dd_html = ""
        if a["dd_max"]:
            floor = cap - a["dd_max"]
            margin = bal - floor
            pctm = max(0.0, min(100.0, 100.0 * margin / a["dd_max"])) if a["dd_max"] else 0
            col = "var(--grn)" if pctm > 50 else ("var(--gold)" if pctm > 25 else "var(--red)")
            dd_html = (f'<div class="note">Plancher DD : <b>{money(floor)} $</b> \u00b7 '
                       f'Marge restante : <b style="color:{col}">{money(margin)} $</b> / {money(a["dd_max"])} $</div>'
                       f'<div style="background:#21262d;border-radius:6px;height:10px;overflow:hidden">'
                       f'<div style="width:{pctm:.1f}%;height:10px;background:{col}"></div></div>')
        acct_cards += (
            f'<div class="card"><h2>{esc(a["name"])} <span style="color:var(--dim);font-size:.7em">'
            f'{esc(a["kind"])}</span></h2>'
            f'<div class="val" style="color:var(--blue)">{money(bal)} $</div>'
            + dd_html +
            f'<form method="post" action="/journal/balance{tok}" style="margin-top:8px">'
            f'<input type="hidden" name="account_id" value="{a["id"]}">'
            f'<input name="balance" placeholder="nouveau solde" inputmode="decimal" '
            f'style="width:140px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;'
            f'border-radius:6px;padding:6px"> '
            f'<button class="btn">Mettre \u00e0 jour</button></form></div>')

    # ── Trades ouverts ──
    def trow(t, closed=False):
        r, of, exits = _trade_r(t)
        ex_txt = " \u00b7 ".join(f"{e.get('label','exit')} {e['price']} ({int(e['frac']*100)}%)" for e in exits) or "\u2014"
        pnl = (t["pnl_usd"] if closed and t["pnl_usd"] is not None
               else (r * (t["risk_usd"] or 0.0)))
        rc = "var(--grn)" if r > 0 else ("var(--red)" if r < 0 else "var(--dim)")
        dev = f'<div class="note">\u26a0\ufe0f D\u00e9viation : {esc(t["deviation"])}</div>' if t["deviation"] else ""
        actions = ""
        if not closed:
            actions = (
                f'<form method="post" action="/journal/trade/{t["id"]}/exit{tok}" style="margin-top:6px">'
                f'<input name="price" placeholder="prix" inputmode="decimal" style="width:90px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:4px"> '
                f'<input name="pct" placeholder="%" inputmode="numeric" style="width:50px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:4px"> '
                f'<input name="label" placeholder="TP1/BE/stop" style="width:90px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:4px"> '
                f'<button class="btn">Sortie partielle</button></form>'
                f'<form method="post" action="/journal/trade/{t["id"]}/close{tok}" style="margin-top:4px">'
                f'<input name="price" placeholder="prix de cl\u00f4ture du reste" inputmode="decimal" style="width:170px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:4px"> '
                f'<button class="btn">Cl\u00f4turer</button></form>')
        when = (t["closed_ts"] or t["opened_ts"] or "")[:16].replace("T", " ")
        return (f'<div class="card"><b>{esc(t["asset"])}</b> \u00b7 {esc(t["side"])} \u00b7 {esc(t["acct"])}'
                f' \u00b7 <span style="color:var(--dim)">{when}</span><br>'
                f'Entr\u00e9e {t["entry"]} \u00b7 SL {t["sl_initial"]} \u00b7 risque {money(t["risk_usd"] or 0)} $'
                f' \u00b7 setup : {esc(t["setup"] or "?")}<br>'
                f'Sorties : {ex_txt}<br>'
                f'<b style="color:{rc}">R = {r:+.2f}</b> \u00b7 P&L indicatif {pnl:+,.0f} $'
                + (f' \u00b7 reste ouvert {int(of*100)}%' if not closed else '')
                + dev + actions + '</div>')

    open_html = "".join(trow(t) for t in open_tr) or '<div class="note">Aucun trade ouvert.</div>'
    closed_html = "".join(trow(t, True) for t in closed_tr) or '<div class="note">Aucun trade cl\u00f4tur\u00e9.</div>'

    # ── Formulaire nouveau trade + pré-remplissage ──
    pre_links = "".join(
        f'<a class="chip" href="/journal{tok}{amp}prefill={r["id"]}">#{r["id"]} {esc(r["asset"] or "?")} '
        f'{esc(r["timeframe"] or "")} @{r["price"]}</a>' for r in recents) or '<span class="note">aucune</span>'
    acct_opts = "".join(f'<option value="{a["id"]}">{esc(a["name"])}</option>' for a in accts)
    inp = 'style="background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;margin:2px;width:130px"'
    form = (
        f'<div class="card"><h2>Nouveau trade</h2>'
        f'<div class="chips">{pre_links}</div>'
        f'<form method="post" action="/journal/trade{tok}">'
        f'<input type="hidden" name="alert_id" value="{pf["alert_id"]}">'
        f'<select name="account_id" {inp}>{acct_opts}</select>'
        f'<input name="asset" placeholder="actif" value="{esc(str(pf["asset"]))}" {inp}>'
        f'<select name="side" {inp}><option{" selected" if pf["side"]=="LONG" else ""}>LONG</option>'
        f'<option{" selected" if pf["side"]=="SHORT" else ""}>SHORT</option></select>'
        f'<input name="entry" placeholder="entr\u00e9e" value="{pf["entry"]}" inputmode="decimal" {inp}>'
        f'<input name="sl" placeholder="SL initial" value="{pf["sl"]}" inputmode="decimal" {inp}>'
        f'<input name="risk_usd" placeholder="risque $" inputmode="decimal" {inp}>'
        f'<input name="setup" placeholder="setup" value="{esc(pf["setup"])}" {inp}>'
        f'<input name="deviation" placeholder="d\u00e9viation vs ticket (pourquoi ?)" style="background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;margin:2px;width:97%">'
        f'<br><button class="btn" style="margin-top:6px">Enregistrer le trade</button></form>'
        f'<div class="note">Pr\u00e9-remplissage : clique une alerte ci-dessus (entr\u00e9e=Fib 1, SL au /sl_fib courant). '
        f'Si tu modifies entr\u00e9e/SL, dis pourquoi dans \u00ab d\u00e9viation \u00bb \u2014 c\u2019est la m\u00e9moire de tes \u00e9carts au plan.</div></div>')

    head = ('<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>FibLab \u2014 Journal</title>' + DASH_CSS + '</head><body>')
    body = ('<h1>\U0001F4D2 Journal de trading</h1>'
            '<div class="sub">R g\u00e9om\u00e9trique broker-agnostique \u00b7 P&L indicatif = R \u00d7 risque \u00b7 '
            'le SOLDE des comptes est ta v\u00e9rit\u00e9, mets-le \u00e0 jour \u00e0 la main.</div>'
            '<div class="grid">' + acct_cards + '</div>'
            + form
            + '<div class="card"><h2>Trades ouverts</h2>' + open_html + '</div>'
            + '<div class="card"><h2>Historique (30 derniers)</h2>' + closed_html + '</div>')
    return head + body + '</body></html>'


@app.route("/journal/balance", methods=["POST"])
def journal_balance():
    if not check_secret():
        return ("unauthorized", 403)
    try:
        aid = int(request.form["account_id"])
        bal = float(request.form["balance"].replace(",", ".").replace(" ", ""))
    except (KeyError, ValueError):
        return ("bad request", 400)
    with db() as conn:
        conn.execute("UPDATE accounts SET balance=? WHERE id=?", (bal, aid))
        conn.commit()
    return redirect("/journal" + _tok())


@app.route("/journal/trade", methods=["POST"])
def journal_trade_new():
    if not check_secret():
        return ("unauthorized", 403)
    f = request.form
    try:
        entry = float(f["entry"].replace(",", "."))
        sl = float(f["sl"].replace(",", "."))
        risk = float((f.get("risk_usd") or "0").replace(",", ".") or 0)
    except (KeyError, ValueError):
        return ("bad request", 400)
    grp = get_asset_group(f.get("asset") or "")
    with db() as conn:
        conn.execute(
            "INSERT INTO trades (account_id,opened_ts,asset,grp,side,entry,sl_initial,"
            "risk_usd,setup,deviation,alert_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (int(f["account_id"]), now_iso(), f.get("asset"), grp,
             f.get("side", "LONG"), entry, sl, risk, f.get("setup"),
             (f.get("deviation") or None), (int(f["alert_id"]) if f.get("alert_id") else None)))
        conn.commit()
    return redirect("/journal" + _tok())


@app.route("/journal/trade/<int:tid>/exit", methods=["POST"])
def journal_trade_exit(tid):
    if not check_secret():
        return ("unauthorized", 403)
    try:
        price = float(request.form["price"].replace(",", "."))
        frac = min(1.0, max(0.01, float(request.form["pct"]) / 100.0))
    except (KeyError, ValueError):
        return ("bad request", 400)
    label = request.form.get("label") or "exit"
    with db() as conn:
        t = conn.execute("SELECT * FROM trades WHERE id=?", (tid,)).fetchone()
        if not t or t["status"] != "open":
            return ("not found", 404)
        exits = json.loads(t["exits"] or "[]")
        already = sum(e["frac"] for e in exits)
        frac = min(frac, max(0.0, 1.0 - already))
        exits.append({"ts": now_iso(), "price": price, "frac": round(frac, 4), "label": label})
        conn.execute("UPDATE trades SET exits=? WHERE id=?", (json.dumps(exits), tid))
        # cl\u00f4ture auto si tout est sorti
        if sum(e["frac"] for e in exits) >= 0.999:
            t2 = conn.execute("SELECT * FROM trades WHERE id=?", (tid,)).fetchone()
            r, _, _ = _trade_r(t2)
            conn.execute("UPDATE trades SET status='closed', closed_ts=?, r_realized=?, pnl_usd=? WHERE id=?",
                         (now_iso(), round(r, 4), round(r * (t["risk_usd"] or 0.0), 2), tid))
        conn.commit()
    return redirect("/journal" + _tok())


@app.route("/journal/trade/<int:tid>/close", methods=["POST"])
def journal_trade_close(tid):
    if not check_secret():
        return ("unauthorized", 403)
    try:
        price = float(request.form["price"].replace(",", "."))
    except (KeyError, ValueError):
        return ("bad request", 400)
    with db() as conn:
        t = conn.execute("SELECT * FROM trades WHERE id=?", (tid,)).fetchone()
        if not t or t["status"] != "open":
            return ("not found", 404)
        exits = json.loads(t["exits"] or "[]")
        rest = max(0.0, 1.0 - sum(e["frac"] for e in exits))
        if rest > 0:
            exits.append({"ts": now_iso(), "price": price, "frac": round(rest, 4), "label": "close"})
        conn.execute("UPDATE trades SET exits=? WHERE id=?", (json.dumps(exits), tid))
        t2 = conn.execute("SELECT * FROM trades WHERE id=?", (tid,)).fetchone()
        r, _, _ = _trade_r(t2)
        conn.execute("UPDATE trades SET status='closed', closed_ts=?, r_realized=?, pnl_usd=? WHERE id=?",
                     (now_iso(), round(r, 4), round(r * (t["risk_usd"] or 0.0), 2), tid))
        conn.commit()
    return redirect("/journal" + _tok())


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
        _rng = PRICE_RANGES.get(group)
        if _rng and parsed.get("price") is not None:
            parsed["_coherence_data"] = (parsed["price"], group, _rng[0], _rng[1])
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
            ticket = build_trade_ticket(parsed, group, get_profile(TELEGRAM_CHAT_ID))
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
