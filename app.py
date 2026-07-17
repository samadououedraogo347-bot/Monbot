import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Flask pour Render
flask_app = Flask(__name__)

# Récupère ton token depuis les variables d'environnement Render
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Crée l'application Telegram
application = Application.builder().token(TOKEN).build()

# Commande /start pour les joueurs
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue ! Entrez le code promo DICAP226 et faites un dépôt minimum de 2000 FCFA pour accéder aux prédictions de 15 jeux."
    )

# Commande /luckyjet réservée à toi (admin)
async def luckyjet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = 6100143894  # ⚠️ Remplace par ton vrai ID Telegram
    if update.message.from_user.id == admin_id:
        await update.message.reply_text("Signaux Lucky Jet : Exemple ✅")
    else:
        await update.message.reply_text("Accès refusé ❌")

# Commande /session <start> <end> <cote> <valeur> [espacement]
async def session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = 6100143894  # ⚠️ Remplace par ton vrai ID Telegram
    if update.message.from_user.id != admin_id:
        await update.message.reply_text("Accès refusé ❌")
        return

    try:
        start_hour = int(context.args[0])   # ex: 7
        end_hour = int(context.args[1])     # ex: 12
        cote = int(context.args[2])         # ex: 2
        valeur = float(context.args[3])     # ex: 1.50
        # Espacement optionnel (par défaut 2 minutes)
        spacing = int(context.args[4]) if len(context.args) > 4 else 2

        # Génère les signaux
        signaux = []
        minute = 0
        while start_hour <= end_hour:
            signaux.append(f"{start_hour:02d}h{minute:02d} → côté {cote} (valeur {valeur})")
            minute += spacing
            if minute >= 60:
                minute = 0
                start_hour += 1

        await update.message.reply_text("📊 Signaux générés :\n" + "\n".join(signaux))

    except Exception:
        await update.message.reply_text("Usage : /session <start> <end> <cote> <valeur> [espacement]")

# Ajoute les commandes
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("luckyjet", luckyjet))
application.add_handler(CommandHandler("session", session))

# Routes Flask pour Render
@flask_app.route('/')
def index():
    return "Bot en ligne ✅"

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "OK"
