# 🤖 FibLab Robot — Guide de déploiement

## Structure des fichiers

```
fiblab-robot/
├── app.py              ← Serveur Flask (parser + scoring + Telegram)
├── requirements.txt    ← Dépendances Python
├── Procfile            ← Démarrage Railway/Gunicorn
├── templates/
│   └── dashboard.html  ← Dashboard web
└── README.md
```

---

## ÉTAPE 1 — Créer le Bot Telegram

1. Ouvre Telegram sur ton téléphone
2. Cherche **@BotFather**
3. Tape `/newbot`
4. Donne un nom : `FibLab Robot`
5. Donne un username : `fiblab_charlie_bot` (ou autre)
6. **Note le TOKEN** → ressemble à `7123456789:AAFxxx...`
7. Envoie `/start` à ton bot
8. Va sur : `https://api.telegram.org/bot<TON_TOKEN>/getUpdates`
9. **Note le `chat_id`** → ressemble à `123456789`

---

## ÉTAPE 2 — Déployer sur Railway

1. Va sur **https://railway.app** → Sign up with GitHub
2. Crée un nouveau projet → **"Deploy from GitHub repo"**
3. Upload ou connecte ce dossier
4. Dans Railway → onglet **Variables** → ajoute :

```
TELEGRAM_TOKEN   = 7123456789:AAFxxx...
TELEGRAM_CHAT_ID = 123456789
```

5. Railway génère une URL automatiquement
   → Exemple : `https://fiblab-robot-production.up.railway.app`

---

## ÉTAPE 3 — Configurer TradingView

1. Ouvre un chart (ex: XAUUSD)
2. Active l'indicateur **Fib Lab - Break/Origin Levels Detector**
3. Crée une alerte :
   - Condition : `Fib Lab - Break/Origin Levels Detector`
   - Type : **Any alert function call**
   - Webhook URL : `https://TON-URL.railway.app/webhook`
   - Message : laisser le défaut de l'indicateur
4. Valide

---

## ÉTAPE 4 — Tester

Ouvre dans ton navigateur :
```
https://TON-URL.railway.app/test
```
→ Tu devrais recevoir un message Telegram de test

Vérifie aussi :
```
https://TON-URL.railway.app/status   ← état du robot
https://TON-URL.railway.app/          ← dashboard
https://TON-URL.railway.app/levels    ← historique JSON
```

---

## Scoring des alertes

| Score | Niveau | Emoji |
|-------|--------|-------|
| 8+    | PRIORITAIRE | 🔴 |
| 5-7   | SECONDAIRE  | ⚠️ |
| < 5   | INFO        | 📊 |

**Détail du scoring :**
- Type Origin Untouched → +5
- Type Origin First Touch → +4
- Type Broken First Touch → +3
- Type Break Created → +2
- Scope Pure → +2
- First Touch → +2
- TF Daily/Weekly → +3
- TF H4/H8/H12 → +2
- TF H1/H2 → +1
