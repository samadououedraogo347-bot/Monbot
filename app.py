import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Commande pour joueurs
def start(update: Update, context: CallbackContext):
    user_text = "Bienvenue ! Entrez le code promo DICAP226 et faites un dépôt minimum de 2000 FCFA pour accéder aux prédictions de 15 jeux."
    update.message.reply_text(user_text)

# Commande spéciale pour toi (admin)
def luckyjet(update: Update, context: CallbackContext):
    admin_id = 123456789  # Remplace par ton ID Telegram
    if update.message.from_user.id == admin_id:
        signaux = "➡️ 15h00 🕒\n➡️ 15h07 🕒\n➡️ 15h16 🕒\n➡️ 15h24 🕒"
        update.message.reply_text(f"Signaux Lucky Jet :\n{signaux}")
    else:
        update.message.reply_text("Accès refusé ❌")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("luckyjet", luckyjet))

@app.route('/')
def index():
    return "OK ✅"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"
