"""
╔══════════════════════════════════════════════════════════════╗
║         FIBLAB ROBOT — Webhook Trading Server  (v2.7.44)     ║
║         Charlie Joe 1972 — Juillet 2026                      ║
║                                                              ║
║  Patch v2.7.44 "Déduplication" :                             ║
║   • Même signal (grp/type/TF/side/niveau ±0.05%) revu dans   ║
║     la fenêtre (48h ou 2 bougies du TF) = stocké muet, sans  ║
║     outcome ni notification — fin des tickets fantômes après ║
║     édition d'alertes TV, stats non double-comptées          ║
║   • Ticket : "1er enregistrement" (honnête) au lieu          ║
║     d'"Origine créée" (la base ne connaît pas la naissance)  ║
║                                                              ║
║  Patch v2.7.43 "Stop par actif×TF" :                         ║
║   • Défauts de stop par (actif, TF) : xau H12 -> Fib -1      ║
║     (stop de survie mesuré +0.27R), xau autres TF -> 0.786   ║
║   • Appliqué aux tickets, à l'éval et au préfill journal     ║
║                                                              ║
║  Patch v2.7.42 "TP Ladder complet" :                         ║
║   • /tp_ladder refondu : filtres asset/tf/type/sl,           ║
║     grille P(TP1..TP4 avant stop) pour 4 niveaux de SL,      ║
║     banc de 5 plans de sortie rejoués (dont 50/20/15/15)     ║
║                                                              ║
║  Patch v2.7.41 "Stop or = 0.786 par défaut" :                ║
║   • SL_FIB_ASSET_DEFAULTS : défauts de stop PAR ACTIF en dur ║
║     (survivent aux redéploiements). xau -> 0.786, mesuré     ║
║     +1.12R sur ACTIVATED H4-H6 (sweep du 05/08)              ║
║   • /sl_fib runtime reste prioritaire pour expérimenter      ║
║                                                              ║
║  Patch v2.7.40 "Sweep SL filtrable" :                        ║
║   • /sl_sweep : ?tf=h4,h6 (filtre TF) et ?type=activated     ║
║     (toute la famille ACTIVATED) — le sweep 0.786/0.5/0.382/ ║
║     0/-1 se lit enfin sur la poche où vit l'edge             ║
║                                                              ║
║  Patch v2.7.39 "Matrice TYPE × TF" :                         ║
║   • Vue croisée type × timeframe au dashboard : R moyen,     ║
║     win rate et n par cellule — répond à "où vit l'edge"     ║
║     (respecte les filtres type/asset ; n<10 estompé)         ║
║                                                              ║
║  Patch v2.7.38 "Range Trendlines = contexte" :               ║
║   • Parser des messages RT (role/approxPrice/tf) du Range    ║
║     Trendlines Detector — stockés SANS outcome : contexte    ║
║     pour la confluence trend à venir, file d'éval épargnée   ║
║   • Jamais notifiés (non-hold -> /ideal les tait)            ║
║                                                              ║
║  Patch v2.7.37 "FIX bouchon HYPE" :                          ║
║   • Twelve Data court-circuité pour HYPE (404 systématique)  ║
║   • Actif sans feed : items expirés >7j -> invalid           ║
║     (anti-bouchon de la tête de file ASC)                    ║
║                                                              ║
║  Patch v2.7.36 "FIX drainage de la file" :                   ║
║   • Tri ASC (anciennes d'abord) dans chaque classe — la file ║
║     se vide par l'arrière ; le DESC moulinait sur les        ║
║     récentes non-résolubles → evaluated=0 chronique          ║
║   • Alertes expirées hors fenêtre feed -> invalid (sinon     ║
║     bouchon éternel en tête de file ASC)                     ║
║                                                              ║
║  Patch v2.7.35 "Éval sélective + garde-fou reeval" :         ║
║   • Éval par priorité : ACTIVATED d'abord, autres Hold,      ║
║     puis standard — non-ACTIVATED plafonnés à 60/run         ║
║     (échantillon témoin) → la file ~5800 ne brûle plus le    ║
║     quota ; les 55 lignes de référence reviennent en 1er     ║
║   • /reeval : 409 sans ?confirm=yes au-delà de 300 évaluées  ║
║   • /tf et /assets : espaces acceptés comme séparateurs      ║
║   (v2.7.27-34 : origin+prox, /prox_gap, date d'origine,      ║
║    zone Fib1→Fib0, %variation, /tf, /move — voir commits)    ║
║                                                              ║
║  Patch v2.7.26 "Alertes au format ticket" + b :              ║
║   • /signaux origin+prox : Origin Hold ACTIVATED + pré-avis  ║
║     ATR Proximity (format INFO uniquement, jamais de ticket  ║
║     — les pré-signaux n'ont pas d'edge, c'est un pré-avis)   ║
║   • Toute alerte notifiée avec géométrie dérivable (entrée + ║
║     Exit) arrive au FORMAT ORDRE LIMITE (entrée/SL/TP1-4/    ║
║     taille du profil) + ligne Score·Side·Scope               ║
║   • Repli sur l'ancien format info si pas de cible           ║
║                                                              ║
║  Patch v2.7.25 "Filtres personnels par destinataire" :       ║
║   • /assets sol,xau | all : ne recevoir que ses actifs       ║
║   • /score 12 : seuil de score minimum personnel             ║
║   • /signaux origin | all : ne recevoir que les Origin Hold  ║
║     ACTIVATED (le seul signal validé) — tickets inclus       ║
║   • Persistés en base, indépendants par chat_id              ║
║                                                              ║
║  Patch v2.7.24 "Risque & capital PAR UTILISATEUR" :          ║
║   • /capital 360000 et /risque 0.5 (alias /risk) : chaque    ║
║     destinataire règle son capital et son % de risque,       ║
║     persistés en base (survivent aux redéploiements)         ║
║   • Le ticket d'ordre est désormais envoyé À CHAQUE          ║
║     destinataire éligible, dimensionné sur SON profil        ║
║     (capital, risque, langue) — plus seulement à l'admin     ║
║   • Garde-fou : risque borné à 5% max                        ║
║                                                              ║
║  Patch v2.7.23 "Journal v2 — modèle Journal De Trading 2026":║
║   • Vue MENSUELLE par compte : $ P&L, % du capital, capital  ║
║     courant, R, leçon, screenshot, totaux (ratio, WR)        ║
║   • Saisie rapide d'un trade clôturé + option "appliquer au  ║
║     solde" ; clôture d'un trade robot avec P&L réel broker   ║
║   • DD propfirm CORRIGÉ : plancher = HWM − DD max (HWM       ║
║     éditable, monté auto quand le solde dépasse)             ║
║   • Équity (P&L cumulé) + stats par stratégie                ║
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
        for _mig in ("ALTER TABLE profiles ADD COLUMN lang TEXT DEFAULT 'fr'",
                     "ALTER TABLE profiles ADD COLUMN capital REAL",
                     "ALTER TABLE profiles ADD COLUMN risk_pct REAL",
                     "ALTER TABLE profiles ADD COLUMN assets TEXT",
                     "ALTER TABLE profiles ADD COLUMN score_min INTEGER",
                     "ALTER TABLE profiles ADD COLUMN signals TEXT",
                     "ALTER TABLE profiles ADD COLUMN tfs TEXT",
                     "ALTER TABLE profiles ADD COLUMN move_min REAL"):
            try:
                conn.execute(_mig)
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
                hwm      REAL,              -- High Water Mark (plancher DD = hwm - dd_max)
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
                [("UFunded", "propfirm", 360000.0, 16000.0, 353064.0),
                 ("Jupiter", "crypto", 0.0, None, 0.0),
                 ("Phantom", "crypto", 0.0, None, 0.0)])
        for mig in ("ALTER TABLE accounts ADD COLUMN hwm REAL",
                    "ALTER TABLE trades ADD COLUMN screenshot TEXT"):
            try:
                conn.execute(mig)
            except Exception:
                pass
        conn.execute("UPDATE accounts SET hwm = 360000.0 WHERE name='UFunded' AND hwm IS NULL")
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
        # v2.7.38 : les messages de CONTEXTE (Range Trendlines) ne sont pas des
        # trades — pas de ligne outcome, la file d'évaluation reste saine.
        if not parsed.get("context_only"):
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
                    "capital":   (row["capital"] if "capital" in row.keys() else None) or TICKET_CAPITAL,
                    "risk_pct":  (row["risk_pct"] if "risk_pct" in row.keys() else None) or TICKET_RISK_PCT,
                    "assets":    (json.loads(row["assets"]) if "assets" in row.keys() and row["assets"] else None),
                    "tfs":       (json.loads(row["tfs"]) if "tfs" in row.keys() and row["tfs"] else None),
                    "move_min":  (row["move_min"] if "move_min" in row.keys() else None) or 0.0,
                    "score_min": (row["score_min"] if "score_min" in row.keys() else None) or 0,
                    "signals":   (row["signals"] if "signals" in row.keys() else None) or "all",
                    "tf_custom": json.loads(row["tf_custom"] or "{}"),
                }
    except Exception as e:
        print(f"[DB] load_profiles : {e}")


def save_profile(chat_id: str, profile: dict):
    with db() as conn:
        conn.execute(
            "INSERT INTO profiles (chat_id,mode,paused,lang,capital,risk_pct,assets,"
            "score_min,signals,tfs,move_min,tf_custom) VALUES (?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(chat_id) DO UPDATE SET "
            "mode=excluded.mode, paused=excluded.paused, lang=excluded.lang, "
            "capital=excluded.capital, risk_pct=excluded.risk_pct, "
            "assets=excluded.assets, score_min=excluded.score_min, "
            "signals=excluded.signals, tfs=excluded.tfs, move_min=excluded.move_min, "
            "tf_custom=excluded.tf_custom",
            (chat_id, profile["mode"], int(profile["paused"]),
             profile.get("lang", "fr"), profile.get("capital", TICKET_CAPITAL),
             profile.get("risk_pct", TICKET_RISK_PCT),
             (json.dumps(profile["assets"]) if profile.get("assets") else None),
             int(profile.get("score_min", 0)), profile.get("signals", "all"),
             (json.dumps(profile["tfs"]) if profile.get("tfs") else None),
             float(profile.get("move_min", 0.0)), json.dumps(profile["tf_custom"]))
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
        "capital": TICKET_CAPITAL,      # v2.7.24 : capital de dimensionnement, par utilisateur
        "risk_pct": TICKET_RISK_PCT,    # v2.7.24 : % de risque par trade, par utilisateur
        "assets": None,                 # v2.7.25 : liste de groupes suivis (None = tous)
        "tfs": None,                    # v2.7.30 : liste de TF suivis (None = selon /mode)
        "move_min": 0.0,                # v2.7.33 : amplitude TP1 minimale en % (0 = off)
        "score_min": 0,                 # v2.7.25 : score minimum pour être notifié
        "signals": "all",               # v2.7.25 : all | origin (Origin Hold ACTIVATED seul)
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
    # ── v2.7.38 : messages Range Trendlines (RT) — CONTEXTE, pas des trades.
    #    Format : 'ORIGIN RT FIRST TOUCH (RT) | role=Support | approxPrice=4176.11 | tf=60'
    if "(RT)" in raw.upper() or " RT " in raw.upper():
        head = raw.split("|")[0].strip()
        result["type"] = re.sub(r"\s*\(RT\)\s*$", "", head).title() + " (RT)"
        result["context_only"] = True
        m = re.search(r'role\s*=\s*(Support|Resistance)', raw, re.IGNORECASE)
        if m:
            result["side"] = m.group(1).capitalize()
        m = re.search(r'approxPrice\s*=\s*([\d.]+)', raw, re.IGNORECASE)
        if m:
            try:
                result["price"] = round(float(m.group(1)), 6)
            except ValueError:
                pass
        m = re.search(r'tf\s*=\s*([0-9]+[A-Za-z]*|[0-9]*[A-Za-z]+)', raw, re.IGNORECASE)
        if m:
            tok = m.group(1)
            if tok.isdigit():
                n = int(tok)
                if n < 60:
                    result["timeframe"] = f"M{n}"
                elif n % 1440 == 0:
                    result["timeframe"] = f"{n // 1440}D" if n > 1440 else "1D"
                elif n % 60 == 0:
                    result["timeframe"] = f"H{n // 60}"
                else:
                    result["timeframe"] = normalize_timeframe(tok)
            else:
                result["timeframe"] = normalize_timeframe(tok)
        return result

    if "ATR PROXIMITY" in raw.upper():
        result["type"] = "ATR Proximity"
        # v2.7.26b : format mono-ligne sans '|' → capturer le token TF seul
        # (l'ancien [^\n\r|]+ avalait toute la fin de ligne).
        m = re.search(r'TF:\s*([0-9]+[A-Za-z]*)', raw, re.IGNORECASE)
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
# v2.7.41 : défauts PAR ACTIF, permanents (survivent aux redéploiements).
# xau -> 0.786 : sweep du 05/08 sur ACTIVATED H4-H6 = +1.12R (vs +0.34R au 0.5).
# /sl_fib <actif> <val> reste prioritaire en runtime pour expérimenter.
SL_FIB_ASSET_DEFAULTS = {"xau": 0.786}
# v2.7.43 : défauts par (actif, TF) — prioritaires sur le défaut actif.
# ("xau","H12") -> -1 : ladder du 05/08 = +0.27R au stop -1 (vs négatif au 0.786) ;
# les stop-outs H12 sont des sweeps de liquidité, pas des invalidations.
SL_FIB_ASSET_TF_DEFAULTS = {("xau", "H12"): -1.0}
robot_state["sl_fib"] = SL_FIB_DEFAULT
# v2.7.20 : surcharge PAR ACTIF (groupe -> fraction). Vide par défaut = tout le
# monde au global. Runtime (reset au redéploiement), comme /ideal et /ticket_tf.
robot_state["sl_fib_asset"] = {}


def sl_fib_for(group, tf=None):
    """Fraction Fibo du stop : surcharge runtime par actif > défaut (actif, TF)
    > défaut actif > réglage global."""
    ov = robot_state.get("sl_fib_asset", {})
    if group in ov:
        return ov[group]
    if tf and (group, (tf or "").upper()) in SL_FIB_ASSET_TF_DEFAULTS:
        return SL_FIB_ASSET_TF_DEFAULTS[(group, tf.upper())]
    if group in SL_FIB_ASSET_DEFAULTS:
        return SL_FIB_ASSET_DEFAULTS[group]
    return robot_state.get("sl_fib", SL_FIB_DEFAULT)


def _ticket_tf_set():
    return TICKET_TF_LARGE if robot_state.get("ticket_tf_mode") == "large" else TICKET_TF_ULTIME


def _ticket_tf_ok(tf):
    return normalize_timeframe(str(tf or "").strip()).upper() in _ticket_tf_set()




# v2.7.30 : équivalences de labels TF (les alertes portent 1D ou D1 selon la source)
_TF_EQUIV = {
    "1D": {"1D", "D1", "D", "DAILY"}, "1W": {"1W", "W1", "W", "WEEKLY"},
    "2D": {"2D", "D2"}, "3D": {"3D", "D3"}, "4D": {"4D", "D4"},
    "5D": {"5D", "D5"}, "6D": {"6D", "D6"}, "7D": {"7D", "D7"},
}


def _tf_expand(tfs):
    out = set()
    for t in tfs:
        out |= _TF_EQUIV.get(t, {t})
    return out


def user_filter(parsed, scoring, group, profile):
    """v2.7.25 — filtres personnels du destinataire. (None, None) = passe."""
    assets = profile.get("assets")
    if assets and group not in assets:
        return False, f"actif '{group}' hors filtre"
    if scoring["score"] < (profile.get("score_min") or 0):
        return False, f"score {scoring['score']} < seuil {profile['score_min']}"
    tfs = profile.get("tfs")
    if tfs and (parsed.get("timeframe") or "").upper() not in _tf_expand(tfs):
        return False, f"TF '{parsed.get('timeframe')}' hors filtre /tf"
    mm = profile.get("move_min") or 0.0
    if mm > 0:
        mv = parsed.get("move_pct")
        if mv is None and parsed.get("price") and parsed.get("target"):
            try:
                mv = 100.0 * abs(parsed["target"] - parsed["price"]) / abs(parsed["price"])
            except (TypeError, ZeroDivisionError):
                mv = None
        # amplitude inconnue -> on laisse passer (ne pas filtrer à l'aveugle)
        if mv is not None and mv < mm:
            return False, f"amplitude {mv:.2f}% < seuil {mm:g}%"
    sig = profile.get("signals")
    atype = (parsed.get("type") or "").lower()
    if sig == "origin" and "origin hold activated" not in atype:
        return False, "filtre 'origin' : type ignoré"
    if sig == "origin+prox" and "origin hold activated" not in atype \
            and "proximity" not in atype:
        return False, "filtre 'origin+prox' : type ignoré"
    return True, None

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
        # v2.7.26b : exemption PRÉ-AVIS du mode /signaux origin+prox — les ATR
        # Proximity passent en INFO (jamais en ticket). PAS un signal tradeable.
        if profile.get("signals") == "origin+prox" and "proximity" in alert_type:
            return True, "ok (pré-avis proximity, mode origin+prox)"
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
        "tk_entry_note": "(Fib 1)", "tk_sl_note": "(Fib {f}, d\u00e9riv\u00e9)",
        "tk_long": "\U0001F7E2 LONG (achat)", "tk_short": "\U0001F534 SHORT (vente)",
        "tk_risk": "Risque", "tk_stop": "Stop", "tk_size": "Taille",
        "tk_size_note": "(specs {g} \u2014 \u00c0 V\u00c9RIFIER)",
        "tk_missing": "obligation manquante \u2014 Fib 0 non d\u00e9rivable, lis sur ton chart",
        "tk_size_hand": "$ \u2014 dimensionne \u00e0 la main",
        "tk_park": "\u23f3 <i>Pose l'ordre et pars : il se d\u00e9clenche seul si le prix revient sur le Fib 1. Sinon pas de trade (un setup qui file sans retest est manqu\u00e9).</i>",
        "tk_chart": "Ouvrir le chart TradingView",
        "tk_demo_warn": "\u26a0\ufe0f <i>D\u00e9mo. V\u00e9rifie la taille (specs broker) avant de poser.</i>",
        "tk_no_order": "\u2014 NE PAS POSER sans v\u00e9rifier l'actif",
        "tk_origin": "1er enregistrement", "tk_origin_unknown": "ant\u00e9rieur au bot",
        "tk_zone": "Zone d'entr\u00e9e : Fib 1 <b>{e}</b> \u2192 Fib 0 <b>{f0}</b> \u2014 au choix dans la zone",
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
        "tk_entry_note": "(Fib 1)", "tk_sl_note": "(Fib {f}, derived)",
        "tk_long": "\U0001F7E2 LONG (buy)", "tk_short": "\U0001F534 SHORT (sell)",
        "tk_risk": "Risk", "tk_stop": "Stop", "tk_size": "Size",
        "tk_size_note": "(specs {g} \u2014 VERIFY)",
        "tk_missing": "missing obligation \u2014 Fib 0 not derivable, read it on your chart",
        "tk_size_hand": "$ \u2014 size it by hand",
        "tk_park": "\u23f3 <i>Park the order and walk away: it fills by itself if price retests Fib 1. No retest, no trade (a setup that runs without retest is a missed one).</i>",
        "tk_chart": "Open the TradingView chart",
        "tk_demo_warn": "\u26a0\ufe0f <i>Demo. Verify the size (broker specs) before parking.</i>",
        "tk_no_order": "\u2014 DO NOT PARK before verifying the asset",
        "tk_origin": "First recorded", "tk_origin_unknown": "predates the bot",
        "tk_zone": "Entry zone: Fib 1 <b>{e}</b> \u2192 Fib 0 <b>{f0}</b> \u2014 your pick within the zone",
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

    elif cmd == "/assets":
        _en = profile.get("lang") == "en"
        _alias = {"sol": "solana", "gold": "xau", "or": "xau", "de30": "dax",
                  "de40": "dax", "bitcoin": "btc", "wbtc": "btc"}
        if arg in ("all", "tous", "tout"):
            profile["assets"] = None
            save_profile(chat_id, profile)
            msg = "\u2705 All assets." if _en else "\u2705 Tous les actifs."
        elif arg:
            toks = [t.strip() for t in " ".join(parts[1:]).replace(";", ",").replace(" ", ",").split(",") if t.strip()]
            groups, bad = [], []
            for t in toks:
                g = _alias.get(t, t)
                (groups if g in ASSET_META else bad).append(g)
            if groups and not bad:
                profile["assets"] = sorted(set(groups))
                save_profile(chat_id, profile)
                lst = ", ".join(profile["assets"])
                msg = (f"\u2705 You will only receive: <b>{lst}</b>" if _en
                       else f"\u2705 Tu ne recevras que : <b>{lst}</b>")
            else:
                ok = ", ".join(sorted(ASSET_META.keys()))
                msg = ((f"\u26a0\ufe0f Unknown: {', '.join(bad)}. Valid: {ok}" if _en
                        else f"\u26a0\ufe0f Inconnu : {', '.join(bad)}. Valides : {ok}") if bad
                       else f"Usage : /assets sol,xau \u00b7 /assets all")
        else:
            cur = ", ".join(profile["assets"]) if profile.get("assets") else ("all" if _en else "tous")
            msg = (f"Assets: <b>{cur}</b>\nUsage : /assets sol,btc \u00b7 /assets all" if _en
                   else f"Actifs suivis : <b>{cur}</b>\nUsage : /assets sol,btc \u00b7 /assets all")

    elif cmd == "/tf":
        _en = profile.get("lang") == "en"
        _canon = {"d": "1D", "d1": "1D", "1d": "1D", "daily": "1D",
                  "w": "1W", "w1": "1W", "1w": "1W", "weekly": "1W",
                  "2d": "2D", "3d": "3D", "4d": "4D", "5d": "5D", "6d": "6D", "7d": "7D"}
        _valid = {"H1", "H2", "H3", "H4", "H6", "H8", "H12",
                  "1D", "2D", "3D", "4D", "5D", "6D", "7D", "1W",
                  "M5", "M15", "M30"}
        if arg in ("all", "tous", "tout"):
            profile["tfs"] = None
            save_profile(chat_id, profile)
            msg = ("\u2705 All timeframes (per /mode)." if _en
                   else "\u2705 Tous les timeframes (selon /mode).")
        elif arg:
            toks = [t.strip().lower() for t in " ".join(parts[1:]).replace(";", ",").replace(" ", ",").split(",") if t.strip()]
            tfs, bad = [], []
            for t in toks:
                c = _canon.get(t, t.upper())
                (tfs if c in _valid else bad).append(c)
            if tfs and not bad:
                profile["tfs"] = sorted(set(tfs))
                save_profile(chat_id, profile)
                lst = ", ".join(profile["tfs"])
                msg = ((f"\u23f1\ufe0f You will only be notified on: <b>{lst}</b>\n"
                        f"\u26a0\ufe0f Also applies within your /mode \u2014 an alert must pass BOTH.")
                       if _en else
                       (f"\u23f1\ufe0f Tu ne seras notifi\u00e9 que sur : <b>{lst}</b>\n"
                        f"\u26a0\ufe0f S'applique EN PLUS de ton /mode \u2014 une alerte doit passer les deux."))
            else:
                ok = "H1 H2 H3 H4 H6 H8 H12 1D 2D 3D 4D 5D 6D 7D 1W (daily/weekly acceptés)"
                msg = ((f"\u26a0\ufe0f Unknown: {', '.join(bad)}. Valid: {ok}" if _en
                        else f"\u26a0\ufe0f Inconnu : {', '.join(bad)}. Valides : {ok}") if bad
                       else "Usage : /tf h12,daily \u00b7 /tf h4,h12,1d \u00b7 /tf all")
        else:
            cur = ", ".join(profile["tfs"]) if profile.get("tfs") else ("all (per /mode)" if _en else "tous (selon /mode)")
            msg = (f"Timeframes: <b>{cur}</b>\nUsage : /tf h12,daily \u00b7 /tf all" if _en
                   else f"Timeframes suivis : <b>{cur}</b>\nUsage : /tf h12,daily \u00b7 /tf all")

    elif cmd == "/move":
        _en = profile.get("lang") == "en"
        try:
            v = float(arg.replace(",", ".").replace("%", ""))
        except (ValueError, AttributeError):
            v = None
        if v is not None and 0 <= v <= 20:
            profile["move_min"] = v
            save_profile(chat_id, profile)
            if v == 0:
                msg = ("\u2705 Amplitude filter off." if _en else "\u2705 Filtre d'amplitude d\u00e9sactiv\u00e9.")
            else:
                msg = ((f"\U0001F4C8 Only alerts with TP1 move \u2265 <b>{v:g}%</b>.\n"
                        f"Note: bigger move \u2260 better edge \u2014 it's capital efficiency "
                        f"(useful without leverage).") if _en else
                       (f"\U0001F4C8 Uniquement les alertes dont l'amplitude TP1 \u2265 <b>{v:g}%</b>.\n"
                        f"Note : plus d'amplitude \u2260 plus d'edge \u2014 c'est de l'efficacit\u00e9 "
                        f"capital (utile sans levier)."))
        else:
            cur = profile.get("move_min", 0.0)
            msg = (f"Minimum TP1 move: <b>{cur:g}%</b>\nUsage : /move 0.5 \u00b7 /move 0 (off)" if _en
                   else f"Amplitude TP1 minimale : <b>{cur:g}%</b>\nUsage : /move 0.5 \u00b7 /move 0 (off)")

    elif cmd == "/score":
        _en = profile.get("lang") == "en"
        try:
            v = int(arg)
        except ValueError:
            v = None
        if v is not None and 0 <= v <= 20:
            profile["score_min"] = v
            save_profile(chat_id, profile)
            msg = (f"\U0001F3AF Minimum score: <b>{v}</b> (0 = everything)." if _en
                   else f"\U0001F3AF Score minimum : <b>{v}</b> (0 = tout).")
        else:
            msg = (f"Current minimum score: <b>{profile.get('score_min', 0)}</b>\nUsage : /score 12 \u00b7 /score 0" if _en
                   else f"Score minimum actuel : <b>{profile.get('score_min', 0)}</b>\nUsage : /score 12 \u00b7 /score 0")

    elif cmd in ("/signaux", "/signals"):
        _en = profile.get("lang") == "en"
        if arg in ("origin", "origine"):
            profile["signals"] = "origin"
            save_profile(chat_id, profile)
            msg = ("\U0001F3AF Only <b>Origin Hold ACTIVATED</b> \u2014 the only validated signal." if _en
                   else "\U0001F3AF Uniquement <b>Origin Hold ACTIVATED</b> \u2014 le seul signal validé.")
        elif arg in ("origin+prox", "origine+prox", "originprox", "origineprox", "prox"):
            profile["signals"] = "origin+prox"
            save_profile(chat_id, profile)
            msg = (("\U0001F3AF <b>Origin Hold ACTIVATED</b> + <b>ATR Proximity</b> heads-up.\n"
                    "\u26a0\ufe0f Proximity = advance warning ONLY (price nearing an origin) \u2014 "
                    "NOT a trade signal. Backtests are clear: pre-signals have no edge.") if _en
                   else ("\U0001F3AF <b>Origin Hold ACTIVATED</b> + pr\u00e9-avis <b>ATR Proximity</b>.\n"
                         "\u26a0\ufe0f Proximity = simple pr\u00e9-avis (le prix approche une origine) \u2014 "
                         "PAS un signal de trade. Les backtests sont formels : les pr\u00e9-signaux n'ont pas d'edge."))
        elif arg in ("all", "tous", "tout"):
            profile["signals"] = "all"
            save_profile(chat_id, profile)
            msg = ("\u2705 All confirmed signals (per /ideal filter)." if _en
                   else "\u2705 Tous les signaux confirmés (selon le filtre /ideal).")
        else:
            cur = profile.get("signals", "all")
            msg = (f"Signals: <b>{cur}</b>\nUsage : /signals origin \u00b7 origin+prox \u00b7 all" if _en
                   else f"Signaux : <b>{cur}</b>\nUsage : /signaux origin \u00b7 origin+prox \u00b7 all")

    elif cmd in ("/capital", "/risque", "/risk"):
        _en = profile.get("lang") == "en"

        def _pfv(s):
            try:
                return float(s.replace(",", ".").replace(" ", "").replace("k", "000").replace("K", "000"))
            except (ValueError, AttributeError):
                return None
        v = _pfv(arg)
        if cmd == "/capital":
            if v is not None and 100 <= v <= 100000000:
                profile["capital"] = v
                save_profile(chat_id, profile)
                r = profile.get("risk_pct", TICKET_RISK_PCT)
                msg = ((f"\U0001F4B0 Capital set to <b>{v:,.0f} $</b> \u2014 tickets sized at "
                        f"{r:g}% = <b>{v*r/100:,.0f} $</b> risk per trade.")
                       if _en else
                       (f"\U0001F4B0 Capital r\u00e9gl\u00e9 \u00e0 <b>{v:,.0f} $</b> \u2014 tickets "
                        f"dimensionn\u00e9s \u00e0 {r:g}% = <b>{v*r/100:,.0f} $</b> de risque par trade.")).replace(",", "\u202f")
            else:
                c = profile.get("capital", TICKET_CAPITAL)
                msg = (f"Current capital: <b>{c:,.0f} $</b>\nUsage : /capital 360000 (ou 360k)"
                       if _en else
                       f"Capital actuel : <b>{c:,.0f} $</b>\nUsage : /capital 360000 (ou 360k)").replace(",", "\u202f")
        else:
            if v is not None and 0.01 <= v <= 5.0:
                profile["risk_pct"] = v
                save_profile(chat_id, profile)
                c = profile.get("capital", TICKET_CAPITAL)
                msg = ((f"\U0001F3AF Risk set to <b>{v:g}%</b> = <b>{c*v/100:,.0f} $</b> per trade "
                        f"(capital {c:,.0f} $).")
                       if _en else
                       (f"\U0001F3AF Risque r\u00e9gl\u00e9 \u00e0 <b>{v:g}%</b> = <b>{c*v/100:,.0f} $</b> par trade "
                        f"(capital {c:,.0f} $).")).replace(",", "\u202f")
            elif v is not None:
                msg = ("\u26a0\ufe0f Risk must be between 0.01% and 5%." if _en
                       else "\u26a0\ufe0f Le risque doit \u00eatre entre 0,01% et 5%.")
            else:
                r = profile.get("risk_pct", TICKET_RISK_PCT)
                msg = (f"Current risk: <b>{r:g}%</b>\nUsage : /risque 0.5 (ou /risk 0.5)"
                       if _en else
                       f"Risque actuel : <b>{r:g}%</b>\nUsage : /risque 0.5 | 1 | 0.3")

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
EVAL_WITNESS_CAP   = 60    # v2.7.35 : non-ACTIVATED max par run (échantillon témoin)
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
    # v2.7.37 : HYPE n'existe pas chez Twelve Data (404 systématique en prod)
    # -> repli Yahoo direct, zéro temps/quota brûlé.
    if group == "hype":
        return None
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
            # v2.7.36 : ASC — les plus ANCIENNES d'abord dans chaque classe :
            # elles sont résolubles (ou expirables) immédiatement, la file se
            # vide par l'arrière au lieu de mouliner sur les récentes en cours.
            "ORDER BY (CASE WHEN LOWER(a.type) LIKE '%activated%' THEN 0 "
            "WHEN LOWER(a.type) LIKE '%hold%' THEN 1 ELSE 2 END), a.id ASC "
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
        # v2.7.35 : échantillon témoin — non-ACTIVATED plafonnés par run
        if "activated" not in (r["type"] or "").lower():
            _nact = sum(1 for g in groups.values() for it in g
                        if "activated" not in (it["r"]["type"] or "").lower())
            if _nact >= EVAL_WITNESS_CAP:
                continue
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
            # v2.7.37 : feed indisponible. Les items expirés depuis > 7 jours ne
            # seront jamais mieux servis -> classés, sinon ils bouchent la tête
            # de file (tri ASC) pour toujours.
            stale = []
            for it in items:
                if now >= it["ts"] + timedelta(hours=it["horizon_h"] + 168):
                    stale.append(("invalid", None, None, None,
                                  "feed indisponible, expiré (v2.7.37)",
                                  now_iso(), it["r"]["id"]))
            if stale:
                with db() as conn:
                    conn.executemany(
                        "UPDATE outcomes SET status=?, mfe_pts=?, mae_pts=?, "
                        "r_realized=?, note=?, updated_ts=? WHERE alert_id=?", stale)
                    conn.commit()
                evaluated += len(stale)
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
                # v2.7.36 : horizon écoulé ET fenêtre de données dépassée -> on
                # ne pourra JAMAIS évaluer ; classer pour vider la file.
                if now >= ts + timedelta(hours=horizon_h) and \
                        (bars and bars[0][0] > end_win):
                    updates.append(("invalid", None, None, None,
                                    "expiré hors fenêtre feed (v2.7.36)", now_iso(), r["id"]))
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
                _slf = sl_fib_for(r["grp"], r["timeframe"])   # v2.7.43 : stop par actif×TF
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


def origin_created_at(grp, price, before_ts=None):
    """v2.7.29 — Timestamp de NAISSANCE d'un niveau : premier événement
    'CREATED' du même groupe au même prix (±0,05%). Fallback : plus ancien
    événement non-ACTIVATED sur ce niveau. None si introuvable (niveau
    antérieur au bot) — on n'invente pas de date."""
    try:
        tol = 0.0005 * max(abs(float(price)), 1e-9)
    except (TypeError, ValueError):
        return None
    with db() as conn:
        row = conn.execute(
            "SELECT ts FROM alerts WHERE grp=? AND price BETWEEN ? AND ? "
            "AND LOWER(type) LIKE '%created%' "
            + ("AND ts < ? " if before_ts else "")
            + "ORDER BY ts ASC LIMIT 1",
            ([grp, price - tol, price + tol] + ([before_ts] if before_ts else []))).fetchone()
        if not row:
            row = conn.execute(
                "SELECT ts FROM alerts WHERE grp=? AND price BETWEEN ? AND ? "
                "AND LOWER(type) NOT LIKE '%activated%' "
                + ("AND ts < ? " if before_ts else "")
                + "ORDER BY ts ASC LIMIT 1",
                ([grp, price - tol, price + tol] + ([before_ts] if before_ts else []))).fetchone()
    return row["ts"] if row else None


def _origin_line(parsed, group, S):
    ts = origin_created_at(group, parsed.get("price"), before_ts=parsed.get("timestamp"))
    if not ts:
        return "<i>" + S["tk_origin_unknown"] + "</i>"
    try:
        d = datetime.fromisoformat(ts)
        if d.tzinfo:
            d = d.astimezone(timezone.utc)
        return "<b>" + d.strftime("%d/%m %H:%M") + " UTC</b>"
    except Exception:
        return "<i>" + S["tk_origin_unknown"] + "</i>"


def build_trade_ticket(parsed, group, profile=None, scoring=None, as_alert=False):
    """ORDRE LIMITE au repos pour les types tradeables (Origin Hold ACTIVATED) :
    limite \u00e0 l'entr\u00e9e (Fib 1), SL = Fib 0 d\u00e9riv\u00e9, ladder de TP d\u00e9riv\u00e9e,
    taille pour un risque fixe. Format pr\u00eat \u00e0 poser, z\u00e9ro surveillance. None si N/A.
    v2.7.26 : as_alert=True (notification au format ticket) contourne les gardes
    TICKET_TYPES/TF — le filtrage a déjà eu lieu en amont (should_notify + profil)."""
    atype = (parsed.get("type") or "").lower()
    if not as_alert:
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
    _cap = float((profile or {}).get("capital") or TICKET_CAPITAL)   # v2.7.24
    _rp  = float((profile or {}).get("risk_pct") or TICKET_RISK_PCT)
    risk_usd  = _cap * _rp / 100.0
    slf = sl_fib_for(group, parsed.get("timeframe"))   # v2.7.43 : actif×TF
    sl = _stop_from_fib(entry, target, long_bias, slf)
    asset = esc(parsed.get("asset") or "?")
    tf    = esc(parsed.get("timeframe") or "?")
    typ   = esc(parsed.get("type") or "")
    dir_txt = S["tk_long"] if long_bias else S["tk_short"]
    hdr = ["\U0001F4CB <b>" + S["tk_title"] + "</b> \u2014 " + S["tk_demo"] + " " + str(int(_cap / 1000)) + "k \u00b7 " + ("%g" % _rp) + "%",]
    if scoring:
        side_e = "\U0001F7E2" if parsed.get("side") == "Support" else "\U0001F534"
        hdr.append(scoring.get("emoji", "") + " " + S["score"] + " <b>" + str(scoring.get("score", "?"))
                   + "</b> \u00b7 " + side_e + " " + esc(parsed.get("side") or "?")
                   + " \u00b7 " + esc(parsed.get("scope") or "?"))
    hdr += [
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

    def _mv(level):
        # v2.7.32 : amplitude prix entrée -> niveau, en % (toujours favorable)
        try:
            return "%.2f%%" % (100.0 * abs(float(level) - entry) / abs(entry))
        except (TypeError, ValueError, ZeroDivisionError):
            return "?"

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
        S["tk_zone"].format(e=entry, f0=_px((entry - unit) if long_bias else (entry + unit))),
        S["tk_origin"] + " : " + _origin_line(parsed, group, S),
        "SL     : <b>" + str(_px(sl)) + "</b> <i>" + S["tk_sl_note"].format(f=("%g" % slf)) + "</i>",
        "TP1 <b>" + str(_px(target)) + "</b> (" + _mv(target) + ") \u00b7 TP2 " + str(_ext(2.618))
        + " \u00b7 TP3 " + str(_ext(3.618)) + " \u00b7 TP4 " + str(_ext(4.618)) + " (" + _mv(_ext(4.618)) + ")",
        bar,
        S["tk_risk"] + " " + str(int(risk_usd)) + " $  \u00b7  " + S["tk_stop"] + " " + str(round(stop, _dec))
        + " pts  \u00b7  R:R 1:" + str(rr) + " (TP1)",
        S["tk_size"] + " <b>" + str(lots) + " lots</b> <i>" + S["tk_size_note"].format(g=group) + "</i>",
        bar,
        "\U0001F4C8 <a href='" + esc(get_tv_link(parsed.get("asset") or "", group)) + "'>" + S["tk_chart"] + "</a>",
        S["tk_demo_warn"]]
    return "\n".join(L)



# ─────────────────────────────────────────────
# JOURNAL DE TRADING v2 (v2.7.23) — modèle "Journal De Trading 2026"
#   vue mensuelle · P&L $ · capital courant · leçons · screenshots ·
#   HWM propfirm (plancher = HWM − DD max) · équity · stats par stratégie
# ─────────────────────────────────────────────
_INP = ('style="background:#0d1117;color:#e6edf3;border:1px solid #30363d;'
        'border-radius:6px;padding:6px;margin:2px"')


def _tok():
    return ("?token=" + WEBHOOK_SECRET) if WEBHOOK_SECRET else ""


def _money(x):
    try:
        return f"{x:,.0f}".replace(",", "\u202f")
    except (TypeError, ValueError):
        return "?"


def _trade_r(t):
    """R réalisé (géométrique) + fraction ouverte, depuis les sorties JSON."""
    try:
        exits = json.loads(t["exits"] or "[]")
    except Exception:
        exits = []
    entry, sl = t["entry"], t["sl_initial"]
    if entry is None or sl is None or entry == sl:
        return None, max(0.0, 1.0 - sum(e.get("frac", 0) for e in exits)), exits
    risk_pts = abs(entry - sl)
    sign = 1.0 if (t["side"] or "").upper() == "LONG" else -1.0
    r = sum(e["frac"] * sign * (e["price"] - entry) / risk_pts for e in exits)
    return r, max(0.0, 1.0 - sum(e["frac"] for e in exits)), exits


def _month_bounds(mstr):
    y, m = int(mstr[:4]), int(mstr[5:7])
    lo = f"{y:04d}-{m:02d}-01"
    y2, m2 = (y + 1, 1) if m == 12 else (y, m + 1)
    return lo, f"{y2:04d}-{m2:02d}-01"


@app.route("/journal", methods=["GET"])
def journal_view():
    if not check_secret():
        return ("unauthorized", 403)
    tok = _tok()
    amp = "&" if tok else "?"
    month = request.args.get("m") or datetime.now(timezone.utc).strftime("%Y-%m")
    acct_f = request.args.get("acct")
    prefill_id = request.args.get("prefill")
    lo, hi = _month_bounds(month)

    with db() as conn:
        accts = conn.execute("SELECT * FROM accounts WHERE active=1 ORDER BY id").fetchall()
        q = ("SELECT t.*, a.name AS acct FROM trades t JOIN accounts a ON a.id=t.account_id "
             "WHERE t.status='closed' AND t.closed_ts >= ? AND t.closed_ts < ? ")
        args = [lo, hi]
        if acct_f:
            q += "AND t.account_id = ? "
            args.append(int(acct_f))
        closed = conn.execute(q + "ORDER BY t.closed_ts", args).fetchall()
        open_tr = conn.execute(
            "SELECT t.*, a.name AS acct FROM trades t JOIN accounts a ON a.id=t.account_id "
            "WHERE t.status='open' ORDER BY t.opened_ts DESC").fetchall()
        all_closed = conn.execute(
            "SELECT t.account_id, t.closed_ts, t.pnl_usd, t.setup, t.asset FROM trades t "
            "WHERE t.status='closed' ORDER BY t.closed_ts").fetchall()
        recents = conn.execute(
            "SELECT id, asset, timeframe, type, side, price, target, grp FROM alerts "
            "WHERE LOWER(type) LIKE '%origin hold activated%' AND price IS NOT NULL "
            "AND target IS NOT NULL ORDER BY id DESC LIMIT 10").fetchall()

    # préremplissage depuis une alerte (mêmes maths que le ticket)
    pf = {"asset": "", "side": "LONG", "entry": "", "sl": "", "setup": "", "alert_id": ""}
    if prefill_id:
        with db() as conn:
            al = conn.execute("SELECT * FROM alerts WHERE id=?", (prefill_id,)).fetchone()
        if al:
            lb = (al["side"] == "Support")
            slv = _stop_from_fib(al["price"], al["target"], lb, sl_fib_for(al["grp"], al["timeframe"]))
            pf = {"asset": al["asset"] or "", "side": "LONG" if lb else "SHORT",
                  "entry": al["price"], "sl": (round(slv, 6) if slv is not None else ""),
                  "setup": f"{al['type']} {al['timeframe'] or ''}".strip(), "alert_id": al["id"]}

    # ═ Cartes comptes (HWM propfirm) ═
    cards = ""
    for a in accts:
        bal = a["balance"] or 0.0
        dd_html = ""
        if a["dd_max"]:
            hwm = a["hwm"] or a["capital"] or 0.0
            floor = hwm - a["dd_max"]
            margin = bal - floor
            pctm = max(0.0, min(100.0, 100.0 * margin / a["dd_max"]))
            col = "var(--grn)" if pctm > 50 else ("var(--gold)" if pctm > 25 else "var(--red)")
            dd_html = (
                f'<div class="note">HWM <b>{_money(hwm)} $</b> \u00b7 plancher <b>{_money(floor)} $</b><br>'
                f'Marge avant violation : <b style="color:{col};font-size:1.15em">{_money(margin)} $</b> / {_money(a["dd_max"])} $</div>'
                f'<div style="background:#21262d;border-radius:6px;height:10px;overflow:hidden">'
                f'<div style="width:{pctm:.1f}%;height:10px;background:{col}"></div></div>'
                f'<form method="post" action="/journal/account{tok}" style="margin-top:6px">'
                f'<input type="hidden" name="account_id" value="{a["id"]}">'
                f'<input name="hwm" placeholder="nouveau HWM" inputmode="decimal" {_INP} size="10">'
                f'<button class="btn">HWM</button></form>')
        cards += (
            f'<div class="card"><h2>{esc(a["name"])} <span style="color:var(--dim);font-size:.68em">{esc(a["kind"])}</span></h2>'
            f'<div class="val" style="color:var(--blue)">{_money(bal)} $</div>' + dd_html +
            f'<form method="post" action="/journal/balance{tok}" style="margin-top:6px">'
            f'<input type="hidden" name="account_id" value="{a["id"]}">'
            f'<input name="balance" placeholder="nouveau solde" inputmode="decimal" {_INP} size="10"> '
            f'<button class="btn">Solde</button></form></div>')

    # ═ Navigation mois + filtre compte ═
    y, m = int(month[:4]), int(month[5:7])
    pm = f"{y-1}-12" if m == 1 else f"{y}-{m-1:02d}"
    nm = f"{y+1}-01" if m == 12 else f"{y}-{m+1:02d}"
    MOIS = ["", "JANVIER", "FÉVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET",
            "AOÛT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DÉCEMBRE"]

    def _u(mm, aa=None):
        aa = acct_f if aa is None else aa
        u = f"/journal{tok}{amp}m={mm}"
        if aa:
            u += f"&acct={aa}"
        return u
    nav = (f'<div class="chips"><a class="chip" href="{_u(pm)}">\u2190 {MOIS[int(pm[5:7])]}</a>'
           f'<span class="chip active">{MOIS[m]} {y}</span>'
           f'<a class="chip" href="{_u(nm)}">{MOIS[int(nm[5:7])]} \u2192</a></div>'
           '<div class="chips"><a class="chip' + ('' if acct_f else ' active') + f'" href="{_u(month, "")}">Tous comptes</a>'
           + "".join(f'<a class="chip{" active" if acct_f == str(a["id"]) else ""}" href="{_u(month, a["id"])}">{esc(a["name"])}</a>'
                     for a in accts) + '</div>')

    # ═ Tableau mensuel (modèle Kasper : P&L $, %, capital courant, leçon, image) ═
    cap_start = None
    if acct_f:
        a0 = next((a for a in accts if str(a["id"]) == acct_f), None)
        if a0:
            future = sum(t["pnl_usd"] or 0 for t in all_closed
                         if t["account_id"] == int(acct_f) and (t["closed_ts"] or "") >= lo)
            cap_start = (a0["balance"] or 0.0) - future
    running = cap_start
    rows_html, tot_p, tot_l, wins, losses = [], 0.0, 0.0, 0, 0
    for i, t in enumerate(closed, 1):
        pnl = t["pnl_usd"] or 0.0
        if pnl >= 0:
            tot_p += pnl; wins += 1
        else:
            tot_l += pnl; losses += 1
        pc = ""
        if running is not None and running > 0:
            pc = f"{100*pnl/running:+.2f}%"
            running += pnl
        r, _, _ = _trade_r(t)
        rtxt = f"{r:+.2f}R" if r is not None else "\u2014"
        col = "var(--grn)" if pnl >= 0 else "var(--red)"
        img = f' \u00b7 <a href="{esc(t["screenshot"])}" target="_blank">\U0001F4F7 chart</a>' if t["screenshot"] else ""
        dev = f'<br><span style="color:var(--gold)">\u26a0\ufe0f {esc(t["deviation"])}</span>' if t["deviation"] else ""
        note = f'<br><span class="note" style="padding:0;border:0;background:none">{esc(t["note"])}</span>' if t["note"] else ""
        rows_html.append(
            f'<tr><td>{i}</td><td>{(t["closed_ts"] or "")[:10]}</td><td><b>{esc(t["asset"] or "?")}</b> {esc(t["side"] or "")}</td>'
            f'<td>{esc(t["setup"] or "?")}</td>'
            f'<td style="font-weight:700;color:{col}">{pnl:+,.0f} $</td>'
            f'<td style="color:{col}">{pc}</td><td>{_money(running) + " $" if running is not None else "\u2014"}</td>'
            f'<td>{rtxt}</td><td style="max-width:230px">{esc(t["acct"])}{img}{dev}{note}</td></tr>')
    n_cl = wins + losses
    wr = f"{100*wins/n_cl:.0f}%" if n_cl else "\u2014"
    ratio = f"{(tot_p/abs(tot_l)):.2f}" if tot_l else "\u221e" if tot_p else "\u2014"
    res = tot_p + tot_l
    res_pc = f" ({100*res/cap_start:+.2f}%)" if cap_start else ""
    month_tbl = (
        '<div class="card"><h2>' + MOIS[m] + f' {y}' + (f' \u2014 capital d\u00e9part {_money(cap_start)} $' if cap_start else '') + '</h2>'
        '<table><thead><tr><th>#</th><th>Date</th><th>Trade</th><th>Strat\u00e9gie</th><th>$ P&L</th>'
        '<th>%</th><th>Capital</th><th>R</th><th>Compte \u00b7 le\u00e7on</th></tr></thead><tbody>'
        + ("".join(rows_html) or '<tr><td colspan="9" class="note">Aucun trade cl\u00f4tur\u00e9 ce mois.</td></tr>')
        + '</tbody></table>'
        + f'<div class="note" style="margin-top:8px"><b>R\u00e9sultat : <span style="color:{"var(--grn)" if res>=0 else "var(--red)"}">{res:+,.0f} $</span>{res_pc}</b>'
          f' \u00b7 profits {tot_p:+,.0f} \u00b7 pertes {tot_l:+,.0f} \u00b7 ratio {ratio}'
          f' \u00b7 win rate {wr} ({wins}W/{losses}L)</div></div>')

    # ═ Équity (cumul P&L clôturés, tous mois) ═
    eq_pts, cum = [], 0.0
    for t in all_closed:
        if acct_f and t["account_id"] != int(acct_f):
            continue
        cum += t["pnl_usd"] or 0.0
        eq_pts.append(cum)
    eq_html = ""
    if len(eq_pts) >= 2:
        w, h = 700, 120
        mn, mx = min(min(eq_pts), 0), max(max(eq_pts), 0)
        rng = (mx - mn) or 1
        pts = " ".join(f"{i*w/(len(eq_pts)-1):.1f},{h-(v-mn)/rng*h:.1f}" for i, v in enumerate(eq_pts))
        zero_y = h - (0 - mn) / rng * h
        eq_html = ('<div class="card"><h2>\u00c9quity \u2014 P&L cumul\u00e9 (' + str(len(eq_pts)) + ' trades)</h2>'
                   f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto">'
                   f'<line x1="0" y1="{zero_y:.1f}" x2="{w}" y2="{zero_y:.1f}" stroke="#30363d" stroke-dasharray="4 4"/>'
                   f'<polyline points="{pts}" fill="none" stroke="{"#3fb950" if cum >= 0 else "#f85149"}" stroke-width="2"/></svg>'
                   f'<div class="note">Cumul : <b>{cum:+,.0f} $</b> (P&L saisis \u2014 le solde des comptes reste ta v\u00e9rit\u00e9)</div></div>')

    # ═ Stats par stratégie ═
    strat = {}
    for t in all_closed:
        if acct_f and t["account_id"] != int(acct_f):
            continue
        k = (t["setup"] or "?").strip() or "?"
        d = strat.setdefault(k, {"n": 0, "w": 0, "pnl": 0.0})
        d["n"] += 1
        d["pnl"] += t["pnl_usd"] or 0.0
        if (t["pnl_usd"] or 0) >= 0:
            d["w"] += 1
    strat_rows = "".join(
        f'<tr><td>{esc(k)}</td><td>{d["n"]}</td><td>{100*d["w"]/d["n"]:.0f}%</td>'
        f'<td style="color:{"var(--grn)" if d["pnl"]>=0 else "var(--red)"};font-weight:700">{d["pnl"]:+,.0f} $</td></tr>'
        for k, d in sorted(strat.items(), key=lambda x: -x[1]["pnl"]))
    strat_html = ('<div class="card"><h2>Par strat\u00e9gie</h2><table><thead><tr><th>Strat\u00e9gie</th>'
                  '<th>N</th><th>Win rate</th><th>P&L</th></tr></thead><tbody>' + strat_rows
                  + '</tbody></table></div>') if strat_rows else ""

    # ═ Formulaires : saisie rapide clôturé + trade ouvert (prefill robot) ═
    acct_opts = "".join(f'<option value="{a["id"]}">{esc(a["name"])}</option>' for a in accts)
    quick = (
        f'<div class="card"><h2>\u270f\ufe0f Trade clôturé (saisie rapide)</h2>'
        f'<form method="post" action="/journal/trade_closed{tok}">'
        f'<select name="account_id" {_INP}>{acct_opts}</select>'
        f'<input name="asset" placeholder="actif" {_INP} size="9">'
        f'<select name="side" {_INP}><option>LONG</option><option>SHORT</option></select>'
        f'<input name="setup" placeholder="strat\u00e9gie / setup" {_INP} size="18">'
        f'<input name="pnl" placeholder="$ P&L (\u2212 si perte)" inputmode="decimal" {_INP} size="12">'
        f'<input name="date" placeholder="AAAA-MM-JJ (vide=auj.)" {_INP} size="14">'
        f'<input name="screenshot" placeholder="lien screenshot TradingView" {_INP} size="26">'
        f'<input name="note" placeholder="commentaire / le\u00e7on" {_INP} style="width:96%">'
        f'<label class="note" style="display:block;margin:4px 0">'
        f'<input type="checkbox" name="apply_balance" value="1" checked> appliquer au solde du compte</label>'
        f'<button class="btn">Enregistrer</button></form></div>')
    pre_links = "".join(
        f'<a class="chip" href="/journal{tok}{amp}m={month}{"&acct="+acct_f if acct_f else ""}&prefill={r["id"]}">'
        f'#{r["id"]} {esc(r["asset"] or "?")} {esc(r["timeframe"] or "")} @{r["price"]}</a>' for r in recents)
    open_form = (
        f'<div class="card"><h2>\U0001F4CB Trade ouvert (depuis un ticket du robot)</h2>'
        f'<div class="chips">{pre_links or "<span class=note>aucune alerte ticketable r\u00e9cente</span>"}</div>'
        f'<form method="post" action="/journal/trade{tok}">'
        f'<input type="hidden" name="alert_id" value="{pf["alert_id"]}">'
        f'<select name="account_id" {_INP}>{acct_opts}</select>'
        f'<input name="asset" placeholder="actif" value="{esc(str(pf["asset"]))}" {_INP} size="9">'
        f'<select name="side" {_INP}><option{" selected" if pf["side"]=="LONG" else ""}>LONG</option>'
        f'<option{" selected" if pf["side"]=="SHORT" else ""}>SHORT</option></select>'
        f'<input name="entry" placeholder="entr\u00e9e" value="{pf["entry"]}" inputmode="decimal" {_INP} size="9">'
        f'<input name="sl" placeholder="SL" value="{pf["sl"]}" inputmode="decimal" {_INP} size="9">'
        f'<input name="risk_usd" placeholder="risque $" inputmode="decimal" {_INP} size="8">'
        f'<input name="setup" placeholder="setup" value="{esc(pf["setup"])}" {_INP} size="20">'
        f'<input name="deviation" placeholder="d\u00e9viation vs ticket \u2014 pourquoi ?" {_INP} style="width:96%">'
        f'<button class="btn" style="margin-top:4px">Ouvrir le trade</button></form></div>')

    # ═ Trades ouverts ═
    op_html = ""
    for t in open_tr:
        r, of, exits = _trade_r(t)
        ex_txt = " \u00b7 ".join(f'{e.get("label","exit")} {e["price"]} ({int(e["frac"]*100)}%)' for e in exits) or "\u2014"
        rtxt = f"{r:+.2f}R" if r is not None else "?"
        op_html += (
            f'<div class="card"><b>{esc(t["asset"])}</b> {esc(t["side"])} \u00b7 {esc(t["acct"])} \u00b7 '
            f'entr\u00e9e {t["entry"]} \u00b7 SL {t["sl_initial"]} \u00b7 risque {_money(t["risk_usd"] or 0)} $'
            f'<br>Sorties : {ex_txt} \u00b7 <b>{rtxt}</b> \u00b7 reste {int(of*100)}%'
            + (f'<br><span style="color:var(--gold)">\u26a0\ufe0f {esc(t["deviation"])}</span>' if t["deviation"] else "")
            + f'<form method="post" action="/journal/trade/{t["id"]}/exit{tok}" style="margin-top:6px">'
              f'<input name="price" placeholder="prix" inputmode="decimal" {_INP} size="8">'
              f'<input name="pct" placeholder="%" inputmode="numeric" {_INP} size="4">'
              f'<input name="label" placeholder="TP1/BE" {_INP} size="7">'
              f'<button class="btn">Sortie partielle</button></form>'
              f'<form method="post" action="/journal/trade/{t["id"]}/close{tok}" style="margin-top:4px">'
              f'<input name="price" placeholder="prix du reste" inputmode="decimal" {_INP} size="10">'
              f'<input name="pnl" placeholder="$ P&L r\u00e9el (broker)" inputmode="decimal" {_INP} size="12">'
              f'<input name="note" placeholder="le\u00e7on" {_INP} size="16">'
              f'<label class="note"><input type="checkbox" name="apply_balance" value="1" checked> \u2192 solde</label> '
              f'<button class="btn">Cl\u00f4turer</button></form></div>')
    open_sec = f'<div class="card"><h2>Trades ouverts ({len(open_tr)})</h2>{op_html}</div>' if open_tr else ""

    head = ('<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>FibLab \u2014 Journal</title>' + DASH_CSS + '</head><body>')
    body = ('<h1>\U0001F4D2 Journal de trading</h1>'
            '<div class="sub">P&L en $ = ta saisie (v\u00e9rit\u00e9 broker) \u00b7 % et capital courant calcul\u00e9s \u00b7 '
            'R affich\u00e9 quand entr\u00e9e/SL connus.</div>'
            '<div class="grid">' + cards + '</div>' + nav + month_tbl + open_sec
            + quick + open_form + eq_html + strat_html)
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
        conn.execute("UPDATE accounts SET hwm=? WHERE id=? AND dd_max IS NOT NULL "
                     "AND (hwm IS NULL OR hwm < ?)", (bal, aid, bal))
        conn.commit()
    return redirect("/journal" + _tok())


@app.route("/journal/account", methods=["POST"])
def journal_account():
    if not check_secret():
        return ("unauthorized", 403)
    try:
        aid = int(request.form["account_id"])
        hwm = float(request.form["hwm"].replace(",", ".").replace(" ", ""))
    except (KeyError, ValueError):
        return ("bad request", 400)
    with db() as conn:
        conn.execute("UPDATE accounts SET hwm=? WHERE id=?", (hwm, aid))
        conn.commit()
    return redirect("/journal" + _tok())


@app.route("/journal/trade_closed", methods=["POST"])
def journal_trade_closed():
    """Saisie rapide d'un trade déjà clôturé (le flux principal du modèle 2026)."""
    if not check_secret():
        return ("unauthorized", 403)
    f = request.form
    try:
        pnl = float(f["pnl"].replace(",", ".").replace(" ", ""))
        aid = int(f["account_id"])
    except (KeyError, ValueError):
        return ("bad request", 400)
    d = (f.get("date") or "").strip()
    ts = (d + "T12:00:00+00:00") if re.match(r"^\d{4}-\d{2}-\d{2}$", d) else now_iso()
    with db() as conn:
        conn.execute(
            "INSERT INTO trades (account_id,opened_ts,closed_ts,asset,grp,side,setup,"
            "pnl_usd,status,note,screenshot) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (aid, ts, ts, f.get("asset"), get_asset_group(f.get("asset") or ""),
             f.get("side", "LONG"), f.get("setup"), pnl, "closed",
             (f.get("note") or None), (f.get("screenshot") or None)))
        if f.get("apply_balance"):
            conn.execute("UPDATE accounts SET balance = COALESCE(balance,0) + ? WHERE id=?", (pnl, aid))
            conn.execute("UPDATE accounts SET hwm=balance WHERE id=? AND dd_max IS NOT NULL "
                         "AND (hwm IS NULL OR hwm < balance)", (aid,))
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
    with db() as conn:
        conn.execute(
            "INSERT INTO trades (account_id,opened_ts,asset,grp,side,entry,sl_initial,"
            "risk_usd,setup,deviation,alert_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (int(f["account_id"]), now_iso(), f.get("asset"),
             get_asset_group(f.get("asset") or ""), f.get("side", "LONG"), entry, sl,
             risk, f.get("setup"), (f.get("deviation") or None),
             (int(f["alert_id"]) if f.get("alert_id") else None)))
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
    with db() as conn:
        t = conn.execute("SELECT * FROM trades WHERE id=? AND status='open'", (tid,)).fetchone()
        if not t:
            return ("not found", 404)
        exits = json.loads(t["exits"] or "[]")
        frac = min(frac, max(0.0, 1.0 - sum(e["frac"] for e in exits)))
        exits.append({"ts": now_iso(), "price": price, "frac": round(frac, 4),
                      "label": request.form.get("label") or "exit"})
        conn.execute("UPDATE trades SET exits=? WHERE id=?", (json.dumps(exits), tid))
        conn.commit()
    return redirect("/journal" + _tok())


@app.route("/journal/trade/<int:tid>/close", methods=["POST"])
def journal_trade_close(tid):
    """Clôture : prix du reste + P&L $ réel optionnel (prioritaire sur R×risque)."""
    if not check_secret():
        return ("unauthorized", 403)
    f = request.form
    with db() as conn:
        t = conn.execute("SELECT * FROM trades WHERE id=? AND status='open'", (tid,)).fetchone()
        if not t:
            return ("not found", 404)
        exits = json.loads(t["exits"] or "[]")
        rest = max(0.0, 1.0 - sum(e["frac"] for e in exits))
        if rest > 0 and f.get("price"):
            try:
                exits.append({"ts": now_iso(), "price": float(f["price"].replace(",", ".")),
                              "frac": round(rest, 4), "label": "close"})
            except ValueError:
                pass
        conn.execute("UPDATE trades SET exits=? WHERE id=?", (json.dumps(exits), tid))
        t2 = conn.execute("SELECT * FROM trades WHERE id=?", (tid,)).fetchone()
        r, _, _ = _trade_r(t2)
        pnl = None
        if f.get("pnl"):
            try:
                pnl = float(f["pnl"].replace(",", ".").replace(" ", ""))
            except ValueError:
                pnl = None
        if pnl is None:
            pnl = round((r or 0.0) * (t["risk_usd"] or 0.0), 2)
        conn.execute(
            "UPDATE trades SET status='closed', closed_ts=?, r_realized=?, pnl_usd=?, "
            "note=COALESCE(?, note) WHERE id=?",
            (now_iso(), (round(r, 4) if r is not None else None), pnl,
             (f.get("note") or None), tid))
        if f.get("apply_balance"):
            conn.execute("UPDATE accounts SET balance = COALESCE(balance,0) + ? WHERE id=?",
                         (pnl, t["account_id"]))
            conn.execute("UPDATE accounts SET hwm=balance WHERE id=? AND dd_max IS NOT NULL "
                         "AND (hwm IS NULL OR hwm < balance)", (t["account_id"],))
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

    # ── v2.7.44 : DÉDUPLICATION — l'indicateur ré-émet le même état à chaque
    #    clôture revalidante (et toute édition d'alerte TV réinitialise son
    #    état -> salve de re-signaux). Même (grp, type, TF, side, niveau
    #    ±0.05%) déjà vu dans la fenêtre = stocké pour traçabilité mais SANS
    #    outcome (ne double-compte pas les stats) et SANS notification.
    is_dup = False
    if parsed.get("price") is not None and not parsed.get("context_only"):
        _tfh = tf_hours(parsed.get("timeframe"))
        _win_h = max(48, 2 * _tfh)          # 48h mini, 2 bougies du TF sinon
        _tol = 0.0005 * abs(parsed["price"])
        _since = (datetime.now(timezone.utc) - timedelta(hours=_win_h)).isoformat()
        try:
            with db() as conn:
                _d = conn.execute(
                    "SELECT id FROM alerts WHERE grp=? AND type=? "
                    "AND COALESCE(timeframe,'')=COALESCE(?,'') AND COALESCE(side,'')=COALESCE(?,'') "
                    "AND price BETWEEN ? AND ? AND ts >= ? LIMIT 1",
                    (group, parsed.get("type"), parsed.get("timeframe"), parsed.get("side"),
                     parsed["price"] - _tol, parsed["price"] + _tol, _since)).fetchone()
            is_dup = _d is not None
        except Exception as e:
            print(f"[DEDUP] {e}")
    if is_dup:
        parsed["context_only"] = True       # stocké sans outcome
        try:
            alert_id = save_alert(parsed, scoring, group)
        except Exception as e:
            print(f"[DB] save_alert : {e}")
            alert_id = None
        print(f"[WEBHOOK] DOUBLON ignoré (fenêtre {_win_h}h) id={alert_id} "
              f"{parsed.get('type')} {parsed.get('asset')} @{parsed.get('price')}")
        return jsonify({"status": "duplicate", "id": alert_id}), 200

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
        ok_f, why_f = user_filter(parsed, scoring, group, profile)   # v2.7.25
        if not ok_f:
            results[user_id] = f"filtré: {why_f}"
            continue
        if user_id == TELEGRAM_CHAT_ID_2 and scoring["level"] != "PRIORITAIRE":
            continue
        if (TICKET_ENABLED
                and any(t in (parsed.get("type") or "").lower() for t in TICKET_TYPES)
                and _ticket_tf_ok(parsed.get("timeframe"))):
            # v2.7.24 : ticket PERSONNALISÉ (capital, risque, langue du profil)
            try:
                tk = build_trade_ticket(parsed, group, profile, scoring=scoring)
                if tk and send_telegram(tk, user_id):
                    results[user_id] = "-> ticket \u2705"
                else:
                    results[user_id] = "-> ticket \u274c"
            except Exception as e:
                results[user_id] = f"ticket err: {e}"
            continue
        notify, reason = should_notify(parsed, scoring, profile)
        if not notify:
            results[user_id] = f"filtré: {reason}"
            continue
        # v2.7.26 : les alertes notifiées prennent le FORMAT TICKET dès que la
        # géométrie Fibo est dérivable (entrée + Exit) ; repli sur le format
        # info sinon (ATR, messages sans cible...).
        tg_msg = None
        if parsed.get("price") is not None and parsed.get("target") is not None \
                and "hold" in (parsed.get("type") or "").lower() \
                and "proximity" not in (parsed.get("type") or "").lower():
            try:
                tg_msg = build_trade_ticket(parsed, group, profile, scoring=scoring, as_alert=True)
            except Exception as e:
                print(f"[TICKET-FMT] {e}")
        if not tg_msg:
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
    """v2.7.35 : destructif — exige ?confirm=yes au-delà de 300 évaluées
    (incident du 26/07 : reset accidentel de toute la base d'évaluation)."""
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    with db() as conn:
        done = conn.execute("SELECT COUNT(*) AS n FROM outcomes WHERE status != 'pending'").fetchone()["n"]
    if done > 300 and request.args.get("confirm") != "yes":
        return jsonify({"blocked": True, "evaluated_that_would_reset": done,
                        "message": "Reset TOTAL du dashboard. Si voulu : &confirm=yes. "
                                   "Usage normal : après un changement /sl_fib."}), 409
    with db() as conn:
        cur = conn.execute(
            "UPDATE outcomes SET status='pending', mfe_pts=NULL, mae_pts=NULL, "
            "r_realized=NULL, note=NULL WHERE status != 'pending'"
        )
        conn.commit()
        n = cur.rowcount
    return jsonify({"reset_to_pending": n})


@app.route("/fix_tf", methods=["GET", "POST"])
def fix_tf_route():
    """v2.7.17 — Nettoyage one-shot du bug TF (pré-v2.7.14) : les Hold
    Daily→7D avaient leur TF tronqué en M1..M5 / '6' / '7'. Remappe ces
    lignes vers 1D..7D et remet leurs outcomes en pending (l'ancienne éval
    portait sur un horizon faux). Limité aux types hold : un éventuel vrai
    hold minute serait remappé à tort — assumé, aucun n'est attendu.
    NB : les gros TF resteront majoritairement non mesurables par le proxy
    (horizon 21j) — c'est la correction d'étiquette qui compte, pas l'éval."""
    if not check_secret():
        return jsonify({"error": "unauthorized"}), 403
    remap = {"M1": "1D", "M2": "2D", "M3": "3D", "M4": "4D", "M5": "5D",
             "6": "6D", "7": "7D"}
    fixed = {}
    with db() as conn:
        ids_all = []
        for old, new in remap.items():
            rows = conn.execute(
                "SELECT id FROM alerts WHERE timeframe = ? AND LOWER(type) LIKE '%hold%'",
                (old,)).fetchall()
            ids = [r["id"] for r in rows]
            if not ids:
                continue
            conn.execute(
                "UPDATE alerts SET timeframe = ? WHERE id IN (%s)"
                % ",".join("?" * len(ids)), [new] + ids)
            fixed[old + "->" + new] = len(ids)
            ids_all += ids
        if ids_all:
            conn.execute(
                "UPDATE outcomes SET status='pending', mfe_pts=NULL, mae_pts=NULL, "
                "r_realized=NULL, note=NULL WHERE alert_id IN (%s)"
                % ",".join("?" * len(ids_all)), ids_all)
        conn.commit()
    return jsonify({"remapped": fixed, "total": len(ids_all),
                    "outcomes_reset_to_pending": len(ids_all)})


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
        "how": "\u2753 Comment lire ce bloc",
        "help_cards": "Ces chiffres viennent du <b>proxy</b> (simulation sur prix historiques), PAS de ton P&L réel. \u00c9valuées = alertes ayant abouti à win ou loss. <b>Ignore le win rate et le R globaux</b> : ils mélangent des types incomparables (pré-signaux gonflés inclus). La vérité est dans \u00ab Espérance par type \u00bb, ligne Origin Hold ACTIVATED.",
        "help_type": "<b>Piège majeur :</b> ARMED / PROXIMITY / CREATED affichent des win rates énormes par <b>artefact de mesure</b> (ils \u00ab gagnent \u00bb en prenant de l'avance avant de savoir si le niveau tient). <b>Ne PAS les trader.</b> Le seul signal validé est <b>Origin Hold ACTIVATED</b> (rejet confirmé par englobante clôturée).",
        "help_exp": "R moyen = espérance par trade <b>au stop courant /sl_fib</b> (défaut 0,5 entre entrée et Fib 0). Ta ligne de référence : <b>Origin Hold ACTIVATED</b>. Calibration connue : ~+0,07R à Fib 0, ~+0,18R à Fib 0,5 \u2014 edge réel mais mince ; spread/slippage non simulés.",
        "help_asset": "Compare les actifs <b>à type de signal égal</b> (utilise le filtre type). Pollution connue : avant le 10/07, des alertes XAU ont été rangées en SOLANA (bug ?asset=), et des doublons existent. Les petits N (&lt;20) ne prouvent rien.",
        "help_tf": "<b>Labels M1\u2013M5, 6, 7 = résidus d'un bug</b> (avant v2.7.14, les Hold Daily\u21927D étaient tronqués en minutes et évalués sur un horizon faux \u2014 leurs stats sont doublement invalides). Nettoyage : route /fix_tf. Par ailleurs les <b>gros TF (Daily\u2192Weekly) ne sont PAS mesurables</b> par le proxy (horizon plafonné 21j) : seules les barres intraday H1\u2192H12 avec N&ge;20 sont interprétables.",
        "help_detail": "Même donnée que le graphe par score, en tableau. Règle : N &lt; 5 = anecdote, pas statistique. Le scoring est sain si le win rate <b>monte</b> avec le score.",
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
        "how": "\u2753 How to read this block",
        "help_cards": "These numbers come from the <b>proxy</b> (simulation on historical prices), NOT your real P&L. Evaluated = alerts resolved to win or loss. <b>Ignore the global win rate and R</b>: they mix incomparable types (inflated pre-signals included). The truth is in \u201cExpectancy by type\u201d, row Origin Hold ACTIVATED.",
        "help_type": "<b>Major trap:</b> ARMED / PROXIMITY / CREATED show huge win rates due to a <b>measurement artefact</b> (they \u201cwin\u201d by taking a free head start before the level is proven). <b>Do NOT trade them.</b> The only validated signal is <b>Origin Hold ACTIVATED</b> (rejection confirmed by a closed engulfing candle).",
        "help_exp": "Mean R = expectancy per trade <b>at the current /sl_fib stop</b> (default 0.5 between entry and Fib 0). Your reference row: <b>Origin Hold ACTIVATED</b>. Known calibration: ~+0.07R at Fib 0, ~+0.18R at Fib 0.5 \u2014 a real but thin edge; spread/slippage not simulated.",
        "help_asset": "Compare assets <b>at equal signal type</b> (use the type filter). Known pollution: before Jul 10, some XAU alerts were filed under SOLANA (?asset= bug), and duplicates exist. Small N (&lt;20) proves nothing.",
        "help_tf": "<b>Labels M1\u2013M5, 6, 7 are bug residue</b> (before v2.7.14, Daily\u21927D Holds were truncated to minutes and evaluated on a wrong horizon \u2014 their stats are doubly invalid). Cleanup: /fix_tf route. Also, <b>large TFs (Daily\u2192Weekly) are NOT measurable</b> by the proxy (21-day horizon cap): only intraday bars H1\u2192H12 with N&ge;20 are interpretable.",
        "help_detail": "Same data as the score chart, as a table. Rule: N &lt; 5 = anecdote, not statistics. Scoring is healthy if win rate <b>rises</b> with score.",
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
    by_cross = {}          # v2.7.39 : (type, tf) -> win/loss/R
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
            # v2.7.39 : matrice croisée TYPE × TF — la vue qui dit OÙ vit l'edge
            _xk = (r["type"] or "?", r["timeframe"] or "?")
            dx = by_cross.setdefault(_xk, {"win": 0, "loss": 0, "rsum": 0.0, "rcnt": 0})
            dx[st] += 1
            rr = r["r_realized"]
            if rr is not None:
                dx["rsum"] += rr
                dx["rcnt"] += 1
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

    def hb(key):
        # v2.7.17 : bloc d'aide repliable, sans JS (details/summary natif)
        return ('<details style="margin:6px 0 10px"><summary style="cursor:pointer;color:var(--dim);font-size:.85em">'
                + T["how"] + '</summary><div class="note" style="margin-top:6px">'
                + T[key] + '</div></details>')

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
    cards += hb("help_cards")
    trows = []
    for r in bs:
        c = "var(--grn)" if r["wr"] >= 50 else "var(--gold)"
        trows.append('<tr><td>' + esc(r["k"]) + '</td><td style="color:var(--grn)">' + str(r["win"])
                     + '</td><td style="color:var(--red)">' + str(r["loss"]) + '</td><td>' + str(r["n"])
                     + '</td><td style="font-weight:700;color:' + c + '">' + str(r["wr"]) + '%</td></tr>')
    table = ('<div class="card"><h2>' + T["detail"] + '</h2>' + hb("help_detail") + '<table><thead><tr>'
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
                 + hb("help_exp")
                 + '<div class="note">' + T["rnote"] + '</div>'
                 + '<table><thead><tr><th>' + T["th_type"] + '</th><th>N</th><th>Win rate</th>'
                 + '<th>' + T["th_rmean"] + '</th><th>' + T["th_rtotal"] + '</th></tr></thead><tbody>'
                 + "".join(exp_rows) + '</tbody></table></div>')

    # ── v2.7.39 : MATRICE TYPE × TF — où vit l'edge, cellule par cellule ──
    _tf_rank = {"M1": 0, "M2": 1, "M3": 2, "M5": 3, "M15": 4, "M30": 5,
                "H1": 10, "H2": 11, "H3": 12, "H4": 13, "H6": 14, "H8": 15,
                "H10": 16, "H12": 17, "1D": 20, "2D": 21, "3D": 22, "4D": 23,
                "5D": 24, "6D": 25, "7D": 26, "1W": 30}
    _x_tfs = sorted({tf for (_t, tf) in by_cross}, key=lambda t: _tf_rank.get(t, 99))
    _x_types = sorted({t for (t, _tf) in by_cross},
                      key=lambda t: ("activated" not in t.lower(), t))
    if by_cross and _x_tfs:
        xh = "".join(f"<th>{esc(t)}</th>" for t in _x_tfs)
        xrows = []
        for ty in _x_types:
            cells = []
            for tf in _x_tfs:
                v = by_cross.get((ty, tf))
                if not v or (v["win"] + v["loss"]) == 0:
                    cells.append('<td style="color:#30363d">·</td>')
                    continue
                n = v["win"] + v["loss"]
                wrx = 100.0 * v["win"] / n
                mr = (v["rsum"] / v["rcnt"]) if v["rcnt"] else 0.0
                col = "var(--grn)" if mr > 0.05 else ("var(--red)" if mr < -0.05 else "var(--gold)")
                dim = ' opacity:.45;' if n < 10 else ''
                cells.append(
                    f'<td style="color:{col};{dim}white-space:nowrap">'
                    f'<b>{mr:+.2f}R</b><br><span style="font-size:.78em;color:var(--dim)">'
                    f'{wrx:.0f}% \u00b7 n={n}</span></td>')
            xrows.append(f'<tr><td style="white-space:nowrap">{esc(ty)}</td>' + "".join(cells) + '</tr>')
        cross_html = ('<div class="card"><h2>' + ("Matrice TYPE \u00d7 TF \u2014 o\u00f9 vit l\u2019edge"
                                                  if lang == "fr" else "TYPE \u00d7 TF matrix \u2014 where the edge lives")
                      + '</h2><div class="note">'
                      + ("Chaque cellule : <b>R moyen</b>, win rate, n. Cellules p\u00e2les = n&lt;10 (peu fiable). "
                         "Rappel : les lignes non-ACTIVATED sont des pr\u00e9-signaux au R gonfl\u00e9 par artefact ; "
                         "les colonnes Daily+ subissent l'horizon d'\u00e9val plafonn\u00e9 (biais loss)."
                         if lang == "fr" else
                         "Each cell: <b>mean R</b>, win rate, n. Faded cells = n&lt;10 (unreliable). "
                         "Non-ACTIVATED rows are pre-signals with artificially inflated R; "
                         "Daily+ columns suffer the capped eval horizon (loss bias).")
                      + '</div><div style="overflow-x:auto"><table><thead><tr><th>Type</th>' + xh
                      + '</tr></thead><tbody>' + "".join(xrows) + '</tbody></table></div></div>')
    else:
        cross_html = ""

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
                   + hb("help_asset")
                   + '<div class="note">' + T["asset_note"] + '</div>'
                   + '<table><thead><tr><th>' + T["th_asset"] + '</th><th>N</th><th>Win rate</th>'
                   + '<th>' + T["th_rmean"] + '</th><th>' + T["th_rtotal"] + '</th></tr></thead><tbody>'
                   + "".join(a_rows) + '</tbody></table></div>') if a_items else ""

    body = (chips + cards
            + '<div class="card"><h2>' + T["by_score"] + '</h2>' + _bar_rows(bs, "#f5a623", T["nodata"]) + '</div>'
            + note
            + '<div class="card"><h2>' + T["by_type"] + '</h2>' + _bar_rows(bt, "#58a6ff", T["nodata"]) + '</div>'
            + exp_table
            + cross_html
            + asset_table
            + '<div class="card"><h2>' + T["by_tf"] + '</h2>' + hb("help_tf") + _bar_rows(btf, "#a78bfa", T["nodata"]) + '</div>'
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
    _type_f = (request.args.get("type") or "origin").lower().strip()
    _like = "%hold activated%" if _type_f == "activated" else "%origin hold activated%"
    with db() as conn:
        rows = conn.execute(
            "SELECT a.id, a.ts, a.asset, a.grp, a.side, a.price, a.timeframe, a.target "
            "FROM alerts a JOIN outcomes o ON a.id = o.alert_id "
            "WHERE a.price IS NOT NULL AND a.side IS NOT NULL AND a.target IS NOT NULL "
            "AND a.ts <= ? AND LOWER(a.type) LIKE ? "
            "ORDER BY a.id DESC LIMIT 500",
            (cutoff, _like)
        ).fetchall()
    _tf_f = set()
    for _t in (request.args.get("tf") or "").upper().replace(" ", ",").split(","):
        _t = _t.strip()
        if _t:
            _tf_f |= _TF_EQUIV.get(_t, {_t})
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
        if _tf_f and (r["timeframe"] or "").upper() not in _tf_f:
            continue
        _af = (request.args.get("asset") or "").lower().strip()
        if _af and (r["grp"] or "").lower() != _af:
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
    _af = (request.args.get("asset") or "").lower().strip()
    _af_lbl = (" \u2014 filtre actif : <b>" + esc(_af.upper()) + "</b>") if _af else ""
    body = ("<h1>\U0001F3AF Sweep de Stop Loss" + _af_lbl + "</h1>"
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


@app.route("/tp_ladder", methods=["GET"])
def tp_ladder():
    """v2.7.42 — Analyse complète de la LADDER TP.
    Filtres : ?asset=xau  ?tf=h4,h6  ?type=origin|activated  ?sl=0.786
    (sl par défaut = le réglage de l'actif). Sorties :
      1) Taux d'atteinte de TP1..TP4 AVANT le stop, pour 4 niveaux de SL
         (0.786 / 0.5 / 0 / -1) — indépendant du plan de sortie.
      2) Banc de 5 plans de sortie rejoués trade par trade au SL choisi :
         A  100% TP1, stop fixe (= l'éval de référence)
         B  25/25/25/25, stop fixe
         C  25/25/25/25, stop remonté (BE après TP1, palier n-1 ensuite)
         D  50/20/15/15, stop remonté (proposition Fred)
         E  60/40 TP1/TP2, stop remonté
    Conservateur : dans une bougie, l'adverse touche AVANT le favorable.
    Reste ouvert en fin d'horizon = soldé au dernier close (M2M)."""
    if not check_secret():
        return ("unauthorized", 403)
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(hours=EVAL_MIN_AGE_H)).isoformat()
    _type_f = (request.args.get("type") or "origin").lower().strip()
    _like = "%hold activated%" if _type_f == "activated" else "%origin hold activated%"
    _af = (request.args.get("asset") or "").lower().strip()
    _tf_f = set()
    for _t in (request.args.get("tf") or "").upper().replace(" ", ",").split(","):
        _t = _t.strip()
        if _t:
            _tf_f |= _TF_EQUIV.get(_t, {_t})
    try:
        _sl_arg = float(request.args.get("sl", ""))
    except ValueError:
        _sl_arg = None

    with db() as conn:
        rows = conn.execute(
            "SELECT a.id, a.ts, a.asset, a.grp, a.side, a.price, a.timeframe, a.target "
            "FROM alerts a JOIN outcomes o ON a.id = o.alert_id "
            "WHERE a.price IS NOT NULL AND a.side IS NOT NULL AND a.target IS NOT NULL "
            "AND a.ts <= ? AND LOWER(a.type) LIKE ? "
            "ORDER BY a.id DESC LIMIT 500",
            (cutoff, _like)
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
        if _af and r["grp"] != _af:
            continue
        if _tf_f and (r["timeframe"] or "").upper() not in _tf_f:
            continue
        key = (r["grp"], r["asset"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append((r, ts))

    TP_MULT = [0.618, 1.618, 2.618, 3.618]
    SL_GRID = [0.786, 0.5, 0.0, -1.0]
    # hit_grid[sl][k] = nb de trades ayant atteint TP(k+1) avant ce stop
    hit_grid = {f: [0, 0, 0, 0] for f in SL_GRID}
    n_grid = 0
    # Plans : (label, poids, trailing)
    PLANS = [("A \u00b7 100% TP1, stop fixe", [1.0, 0, 0, 0], False),
             ("B \u00b7 25\u00d74, stop fixe", [.25, .25, .25, .25], False),
             ("C \u00b7 25\u00d74, stop remont\u00e9", [.25, .25, .25, .25], True),
             ("D \u00b7 50/20/15/15, stop remont\u00e9", [.50, .20, .15, .15], True),
             ("E \u00b7 60/40 TP1-TP2, stop remont\u00e9", [.60, .40, 0, 0], True)]
    plan_sum = [0.0] * len(PLANS)
    plan_win = [0] * len(PLANS)
    n_used = 0
    open_at_horizon = 0
    sl_used_desc = None
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
            slf = _sl_arg if _sl_arg is not None else sl_fib_for(grp)
            sl_used_desc = "%g" % slf
            sdist = (1.0 - slf) * unit
            if sdist <= 0:
                continue
            tf_h = tf_hours(r["timeframe"])
            horizon_h = min(max(EVAL_HORIZON_BARS * tf_h, EVAL_HORIZON_MIN_H), EVAL_HORIZON_MAX_H)
            end_win = min(ts + timedelta(hours=horizon_h), now)
            post = [b for b in bars if ts < b[0] <= end_win]
            if not post:
                continue
            tp_d = [m * unit for m in TP_MULT]

            # ═ 1. Grille P(TPk avant stop) pour les 4 niveaux de SL — plan-agnostique ═
            for f in SL_GRID:
                sd = (1.0 - f) * unit
                khit, stopped = 0, False
                for (_dt, hi, lo, _c) in post:
                    fav = (hi - entry) if long_bias else (entry - lo)
                    adv = (entry - lo) if long_bias else (hi - entry)
                    if adv >= sd:
                        stopped = True
                        break
                    while khit < 4 and fav >= tp_d[khit]:
                        hit_grid[f][khit] += 1
                        khit += 1
                    if khit >= 4:
                        break
            n_grid += 1

            # ═ 2. Banc des 5 plans, au SL choisi ═
            last_close = post[-1][3]
            m2m = ((last_close - entry) if long_bias else (entry - last_close))
            for pi, (_lbl, w, trailing) in enumerate(PLANS):
                hit, c_stop, done, rP = 0, -sdist, False, None
                for (_dt, hi, lo, _c) in post:
                    fav = (hi - entry) if long_bias else (entry - lo)
                    adv = (entry - lo) if long_bias else (hi - entry)
                    if c_stop <= 0:
                        s_hit = adv >= -c_stop
                    else:
                        s_hit = ((entry + c_stop) >= lo) if long_bias else ((entry - c_stop) <= hi)
                    if s_hit:
                        cash = sum(w[i] * tp_d[i] for i in range(hit))
                        rem = sum(w[i] for i in range(hit, 4))
                        rP = (cash + rem * c_stop) / sdist
                        done = True
                        break
                    new_hit = hit
                    while new_hit < 4 and fav >= tp_d[new_hit]:
                        new_hit += 1
                    if new_hit > hit:
                        hit = new_hit
                        if sum(w[i] for i in range(hit, 4)) <= 1e-9:
                            rP = sum(w[i] * tp_d[i] for i in range(4)) / sdist
                            done = True
                            break
                        if trailing:
                            c_stop = 0.0 if hit == 1 else tp_d[hit - 2]
                if not done:
                    cash = sum(w[i] * tp_d[i] for i in range(hit))
                    rem = sum(w[i] for i in range(hit, 4))
                    rP = (cash + rem * m2m) / sdist
                    if pi == 0:
                        open_at_horizon += 1
                plan_sum[pi] += rP
                if rP > 0:
                    plan_win[pi] += 1
            n_used += 1

    # ═ Rendu ═
    title_f = []
    if _af:
        title_f.append(_af.upper())
    if _tf_f:
        title_f.append("/".join(sorted(_tf_f)))
    title_f.append("famille ACTIVATED" if _type_f == "activated" else "Origin Hold ACTIVATED")
    grid_rows = ""
    for k in range(4):
        cells = ""
        for f in SL_GRID:
            p = (100.0 * hit_grid[f][k] / n_grid) if n_grid else 0.0
            rmult = TP_MULT[k] / (1.0 - f)
            col = "var(--grn)" if p >= 50 else ("var(--gold)" if p >= 30 else "var(--dim)")
            cells += (f'<td style="color:{col}"><b>{p:.0f}%</b> '
                      f'<span style="font-size:.78em;color:var(--dim)">({rmult:.2f}R)</span></td>')
        grid_rows += f'<tr><td><b>TP{k+1}</b> ({TP_MULT[k]:.3f}u)</td>{cells}</tr>'
    best = max(range(len(PLANS)), key=lambda i: plan_sum[i]) if n_used else 0
    plan_rows = ""
    for pi, (lbl, _w, _t) in enumerate(PLANS):
        mr = plan_sum[pi] / n_used if n_used else 0.0
        wr = 100.0 * plan_win[pi] / n_used if n_used else 0.0
        hl = ' style="background:rgba(63,185,80,.12)"' if pi == best else ""
        col = "var(--grn)" if mr > 0.05 else ("var(--red)" if mr < -0.05 else "var(--gold)")
        plan_rows += (f'<tr{hl}><td>{lbl}</td><td style="color:{col};font-weight:700">{mr:+.3f}R</td>'
                      f'<td>{wr:.0f}%</td><td style="color:var(--dim)">{plan_sum[pi]:+.1f}R</td></tr>')
    head = ('<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>FibLab \u2014 TP Ladder</title>' + DASH_CSS + '</head><body>')
    body = ('<h1>\U0001F3AF Ladder TP \u2014 ' + esc(" \u00b7 ".join(title_f)) + '</h1>'
            '<div class="sub">' + str(n_used) + ' trades rejou\u00e9s \u00b7 SL du banc de plans : Fib '
            + esc(sl_used_desc or "?") + ' \u00b7 ' + str(open_at_horizon)
            + ' encore ouverts \u00e0 l\u2019horizon (sold\u00e9s M2M)</div>'
            '<div class="card"><h2>Taux d\u2019atteinte des paliers AVANT le stop</h2>'
            '<div class="note">Chaque cellule : % des trades o\u00f9 le palier est atteint avant ce stop, '
            'et (le R que vaut ce palier \u00e0 ce stop). Un stop serr\u00e9 baisse le % mais gonfle le R \u2014 '
            'c\u2019est l\u2019arbitrage \u00e0 lire.</div>'
            '<table><thead><tr><th>Palier</th><th>SL 0.786</th><th>SL 0.5</th><th>SL 0</th><th>SL \u22121</th>'
            '</tr></thead><tbody>' + grid_rows + '</tbody></table></div>'
            '<div class="card"><h2>Banc des plans de sortie (SL Fib ' + esc(sl_used_desc or "?") + ')</h2>'
            '<div class="note">Rejou\u00e9s trade par trade, r\u00e8gle conservatrice. \u00ab stop remont\u00e9 \u00bb '
            '= BE apr\u00e8s TP1, puis palier n\u22121. Ligne verte = meilleure esp\u00e9rance. '
            'Ajoute ?sl=0.5 \u00b7 ?tf=h4,h6 \u00b7 ?type=activated \u00e0 l\u2019URL pour changer le p\u00e9rim\u00e8tre.</div>'
            '<table><thead><tr><th>Plan</th><th>R moyen</th><th>% trades positifs</th><th>R total</th>'
            '</tr></thead><tbody>' + plan_rows + '</tbody></table></div>')
    return head + body + '</body></html>'


@app.route("/prox_gap", methods=["GET"])
def prox_gap():
    """v2.7.28 — Écart pré-avis → signal : pour chaque Origin Hold ACTIVATED,
    retrouve le dernier ATR Proximity sur le MÊME niveau (même groupe, prix à
    ±0,05%, dans les 14 jours précédents) et mesure le délai. Ventilé par TF
    (celui de l'ACTIVATED — fiable) et par actif. Donne aussi le taux de
    conversion des pré-avis (niveaux annoncés qui finissent ACTIVATED).
    Limites : actifs pré-10/07 partiellement mal étiquetés ; doublons
    d'alertes possibles ; TF Daily+ historiques dépendent de /fix_tf."""
    if not check_secret():
        return ("unauthorized", 403)
    with db() as conn:
        prox = conn.execute(
            "SELECT ts, grp, price FROM alerts WHERE LOWER(type) LIKE '%proximity%' "
            "AND price IS NOT NULL ORDER BY ts").fetchall()
        acts = conn.execute(
            "SELECT ts, grp, price, timeframe FROM alerts "
            "WHERE LOWER(type) LIKE '%origin hold activated%' AND price IS NOT NULL "
            "ORDER BY ts").fetchall()

    def _dt(s):
        try:
            d = datetime.fromisoformat(s)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except Exception:
            return None

    P = [(r["grp"], float(r["price"]), _dt(r["ts"])) for r in prox if _dt(r["ts"])]
    gaps_tf, gaps_asset, matched = {}, {}, 0
    for a in acts:
        ta = _dt(a["ts"])
        if not ta:
            continue
        best = None
        for g, p, tp in P:
            if g != a["grp"] or tp >= ta or (ta - tp).days > 14:
                continue
            if abs(p - a["price"]) > 0.0005 * max(abs(a["price"]), 1e-9):
                continue
            if best is None or tp > best:
                best = tp
        if best is None:
            continue
        matched += 1
        gap_h = (ta - best).total_seconds() / 3600.0
        gaps_tf.setdefault(a["timeframe"] or "?", []).append(gap_h)
        gaps_asset.setdefault(a["grp"] or "?", []).append(gap_h)

    # conversion : niveaux pré-annoncés (dédupliqués grp+prix) suivis d'un ACTIVATED
    levels = {}
    for g, p, tp in P:
        k = (g, round(p, 6))
        if k not in levels or tp < levels[k]:
            levels[k] = tp
    conv = {}
    for (g, p), t0 in levels.items():
        d = conv.setdefault(g, {"n": 0, "ok": 0})
        d["n"] += 1
        for a in acts:
            ta = _dt(a["ts"])
            if a["grp"] == g and ta and ta > t0 and (ta - t0).days <= 14 \
                    and abs(float(a["price"]) - p) <= 0.0005 * max(abs(p), 1e-9):
                d["ok"] += 1
                break

    def _med(v):
        s = sorted(v)
        n = len(s)
        return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

    def _fmt_h(h):
        return ("%.0f min" % (h * 60)) if h < 1 else (("%.1f h" % h) if h < 48 else ("%.1f j" % (h / 24)))

    def _tbl(d, label):
        rows = "".join(
            f'<tr><td>{esc(str(k))}</td><td>{len(v)}</td><td><b>{_fmt_h(_med(v))}</b></td>'
            f'<td>{_fmt_h(min(v))}</td><td>{_fmt_h(max(v))}</td></tr>'
            for k, v in sorted(d.items(), key=lambda x: -len(x[1])))
        return ('<div class="card"><h2>D\u00e9lai pr\u00e9-avis \u2192 ACTIVATED par ' + label + '</h2>'
                '<table><thead><tr><th>' + label + '</th><th>N</th><th>M\u00e9diane</th><th>Min</th><th>Max</th>'
                '</tr></thead><tbody>' + (rows or '<tr><td colspan="5" class="note">aucune donn\u00e9e</td></tr>')
                + '</tbody></table></div>')

    conv_rows = "".join(
        f'<tr><td>{esc(g)}</td><td>{d["n"]}</td><td>{d["ok"]}</td>'
        f'<td style="font-weight:700">{100*d["ok"]/d["n"]:.0f}%</td></tr>'
        for g, d in sorted(conv.items(), key=lambda x: -x[1]["n"]))
    head = ('<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>FibLab \u2014 Prox Gap</title>' + DASH_CSS + '</head><body>')
    body = ('<h1>\u23f1\ufe0f Pr\u00e9-avis Proximity \u2192 Origin Hold ACTIVATED</h1>'
            '<div class="sub">' + str(matched) + ' signaux rapproch\u00e9s d\u2019un pr\u00e9-avis '
            '(m\u00eame niveau \u00b10,05%, fen\u00eatre 14 j) \u00b7 ' + str(len(levels))
            + ' niveaux pr\u00e9-annonc\u00e9s au total</div>'
            + _tbl(gaps_tf, "TF") + _tbl(gaps_asset, "actif")
            + '<div class="card"><h2>Taux de conversion des pr\u00e9-avis</h2>'
              '<table><thead><tr><th>Actif</th><th>Niveaux annonc\u00e9s</th><th>Convertis</th><th>%</th>'
              '</tr></thead><tbody>' + (conv_rows or '<tr><td colspan="4" class="note">aucune donn\u00e9e</td></tr>')
            + '</tbody></table>'
              '<div class="note"><b>Lecture :</b> le d\u00e9lai = l\u2019avance que te donne le pr\u00e9-avis pour '
              'pr\u00e9parer la zone. Le taux de conversion = la part des niveaux annonc\u00e9s qui finissent '
              'confirm\u00e9s \u2014 le compl\u00e9ment ne se confirme JAMAIS : raison de plus pour ne jamais '
              'entrer sur un pr\u00e9-avis. Donn\u00e9es pr\u00e9-10/07 : actifs partiellement mal \u00e9tiquet\u00e9s, '
              'doublons possibles \u2014 tendances, pas valeurs grav\u00e9es.</div></div>')
    return head + body + '</body></html>'


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
        "version": "2.7.44",
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
