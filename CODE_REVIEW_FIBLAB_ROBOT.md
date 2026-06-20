# Revue détaillée — FibLab Robot v2.1.0

Ce document rassemble l'audit complet et les recommandations réalisées automatiquement pour le dépôt `fiblab_robot`.

---

## 1. Aperçu général

- Langage : Python 3
- Framework : Flask
- Base de données : SQLite
- Infra : Railway / Gunicorn
- Fichier principal : `app.py`
- Templates : `templates/` (vide dans le dépôt)
- Tests : aucun fichier `tests/`
- CI : aucun workflow GitHub détecté


## 2. Points forts

1. Architecture logique et claire : pipeline Parser → Scoring → Filtrage → Notification.
2. Bonnes pratiques de sécurité appliquées :
   - échappement HTML (`html.escape`) pour les messages Telegram ;
   - authentification du webhook via `WEBHOOK_SECRET`.
3. Persistance raisonnable avec SQLite (tables `alerts`, `outcomes`, `profiles`).
4. Parser robuste : gère plusieurs formats texte/JSON et normalise les timeframes (TF) spécifiques.
5. Scoring multi-critères bien pensé (types, scope, TF, first touch).
6. Filtrage utilisateur par profil (mode swing/scalp/both, TF custom, pause/killswitch).
7. Commandes Telegram complètes et intuitives.


## 3. Points à améliorer (détaillés)

### 3.1. Gestion des erreurs et résilience (critique)

- Problème : envoi Telegram silencieux en cas d'échec (print seulement), pas de retry ou backoff.
- Impact : pertes de notifications en cas d'erreur réseau.
- Recommandation : ajouter retry/backoff (ex. `tenacity`), logger structuré et gestion des erreurs explicite.

### 3.2. SQLite et concurrence

- Problème : connexion SQLite simple sans `check_same_thread=False`, pas de WAL ni de verrou global.
- Impact : risque `database is locked` sous charge concurrente (gunicorn + workers).
- Recommandation : activer `PRAGMA journal_mode=WAL`, utiliser `timeout` et envisager un lock (threading.Lock) pour writes. Si montée en charge importante, migrer vers PostgreSQL.

### 3.3. Fonction `evaluate_pending_outcomes()` non implémentée

- Problème : l'évaluation automatique des outcomes (MFE/MAE, win/loss) est un squelette vide.
- Impact : outcomes restent `pending`, pas de backtest possible, pas d'évaluation du scoring.
- Recommandation : intégrer un price feed (OANDA / broker / TradingView export) ou un endpoint de backtest pour calculer MFE/MAE et déterminer win/loss.

### 3.4. Templates manquants

- Problème : `templates/dashboard.html` absent mais invoqué par `render_template` → crash au chargement du dashboard.
- Recommandation : ajouter un template Jinja2 minimal et vérifier le rendu.

### 3.5. Logging insuffisant

- Problème : `print()` dispersés, pas de niveaux, pas de rotation des logs.
- Recommandation : configurer le module `logging` (StreamHandler + RotatingFileHandler), utiliser `logger.info()`, `logger.error()`.

### 3.6. Historiques en mémoire volatils

- Problème : `alert_history` et `histories` sont en mémoire (deque) et perdus au redémarrage.
- Recommandation : charger les dernières alertes depuis SQLite au démarrage pour restaurer le dashboard.

### 3.7. Rate limiting absent

- Problème : si le secret webhook fuit, possibilité de spam massif.
- Recommandation : ajouter `flask_limiter` (limite par IP ou global, ex. 100/min) et/ou un contrôle d'API key plus strict.

### 3.8. Tests inexistants

- Problème : pas de tests unitaires pour le parser, scorer ou routes.
- Recommandation : ajouter tests pytest pour `parse_fiblab_message`, `compute_score`, `should_notify`, endpoints critiques. Ajouter CI (GitHub Actions) pour exécuter tests sur push/PR.


## 4. Recommandations prioritaires (plan d'action)

P0 — Critique (corriger immédiatement):
1. Créer `templates/dashboard.html` pour éviter le crash du dashboard.
2. Implémenter l'évaluation des outcomes (ou fournir un endpoint de backtest) pour commencer à mesurer le win rate.
3. Ajouter logging structuré.

P1 — Important (avant v3.0.0):
4. Améliorer la robustesse DB (WAL, timeout, lock ; ou migration vers PostgreSQL si besoin).
5. Ajouter retry/backoff pour l'envoi Telegram.
6. Mettre en place un rate limiter sur `/webhook`.
7. Écrire des tests unitaires de base (parser + scoring).

P2 — Améliorations: 
8. Charger alert_history depuis SQLite au démarrage.
9. Ajouter un export CSV des alerts/outcomes pour analyse externe.
10. Monitoring (Sentry, Prometheus, DataDog) et alertes opérationnelles.


## 5. Exemple de correctifs / extraits de code

- Retry Telegram (extrait simplifié) :

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def send_telegram(...):
    # utiliser requests.post(...).raise_for_status()
```

- SQLite safer usage :

```python
import sqlite3
import threading
_db_lock = threading.Lock()

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

# Dans fonctions d'écriture :
with _db_lock:
    # write operations
```

- Chargement historique au démarrage :

```python
def load_alert_history():
    with db() as conn:
        rows = conn.execute("SELECT * FROM alerts ORDER BY ts DESC LIMIT 200").fetchall()
    for r in rows:
        alert_history.appendleft(dict(r))

load_alert_history()
```

- Exemple de test pytest pour le parser :

```python
# tests/test_parser.py
from app import parse_fiblab_message, compute_score

def test_parse_xau_support():
    raw = "Origin First Touch — XAUUSD 2D | Side: Support | Price: 4310.00 | Scope: Pure"
    res = parse_fiblab_message(raw)
    assert res['asset'] == 'XAUUSD'
    assert res['side'] == 'Support'


def test_score_priority():
    parsed = {'type': 'Origin Untouched', 'timeframe': '2D', 'scope': 'Pure'}
    s = compute_score(parsed)
    assert s['level'] == 'PRIORITAIRE'
```


## 6. Scorecard final

- Logique métier : 8/10
- Sécurité : 7/10
- Fiabilité : 6/10
- Maintenabilité : 7/10
- Scalabilité : 5/10

Note globale : ~6.6/10 — Prototype solide mais pas encore prêt pour usage intensif/production.


## 7. Next steps recommandés (ordre suggéré)

1. Correction immédiate du template et du logging
2. Tests unitaires (parser + scoring)
3. Robustification de la DB
4. Implémentation d'un système d'évaluation automatique d'outcomes
5. Monitoring et CI


---

Dernière mise à jour : 2026-06-20

Si tu veux, je peux aussi :
- ouvrir un commit/PR avec ce fichier (c'est en train de se faire),
- ajouter un template Jinja2 minimal,
- créer un fichier `tests/` initial et un workflow GitHub Actions.

