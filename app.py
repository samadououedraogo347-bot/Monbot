import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Flask pour Render
flask_app = Flask(__name__)

# Récupère ton token depuis les variables d'environnement Render
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # URL publique du webhook

# Crée l'application Telegram
application = Application.builder().token(TOKEN).build()

# Flag pour tracker si l'application est initialisée
app_initialized = False

# ⚠️ Remplace ce nombre par TON vrai ID Telegram
admin_id = 6100143894

# Dictionnaires pour gérer les joueurs
joueurs_attente = {}
joueurs_valides = {}

async def initialize_app():
    """Initialise l'application Telegram une seule fois"""
    global app_initialized
    if not app_initialized:
        await application.initialize()
        app_initialized = True
        print("✅ Application Telegram initialisée")

# Commande /start pour les joueurs
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue 👋\n\nPour accéder aux prédictions :\n"
        "1️⃣ Inscris-toi avec le code promo DICAP226\n"
        "2️⃣ Fais un dépôt minimum de 2000 FCFA\n"
        "3️⃣ Envoie ton ID 1win avec la commande /id <ton_id>"
    )

# Commande /id pour envoyer l'ID 1win
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    id_1win = context.args[0] if context.args else None

    if not id_1win:
        await update.message.reply_text("❌ Tu dois entrer ton ID 1win. Exemple : /id 15902784")
        return

    joueurs_attente[user_id] = id_1win
    await update.message.reply_text("⏳ Ton ID a été envoyé pour validation. Attends la confirmation de l'admin.")

# Commande admin pour valider un joueur
async def valider(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != admin_id:
        await update.message.reply_text("Accès refusé ❌")
        return

    try:
        user_id = int(context.args[0])
        if user_id in joueurs_attente:
            joueurs_valides[user_id] = True
            await update.message.reply_text(f"✅ Joueur {user_id} validé. Il a maintenant accès aux jeux.")
        else:
            await update.message.reply_text("❌ Joueur introuvable.")
    except:
        await update.message.reply_text("Usage : /valider <user_id>")

# Commande admin pour refuser un joueur
async def refuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != admin_id:
        await update.message.reply_text("Accès refusé ❌")
        return

    try:
        user_id = int(context.args[0])
        if user_id in joueurs_attente:
            del joueurs_attente[user_id]
            await update.message.reply_text(f"❌ Joueur {user_id} refusé.")
        else:
            await update.message.reply_text("❌ Joueur introuvable.")
    except:
        await update.message.reply_text("Usage : /refuser <user_id>")

# Commande /jeux pour les joueurs validés
async def jeux(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in joueurs_valides:
        await update.message.reply_text("❌ Accès refusé. Ton compte n'est pas validé.")
        return

    await update.message.reply_text(
        "🎮 Voici la liste des 15 jeux disponibles :\n"
        "1. Lucky Jet\n2. Aviator\n3. Mines\n4. Crash\n5. Roulette\n"
        "6. Dice\n7. Blackjack\n8. Poker\n9. Slots\n10. Baccarat\n"
        "11. Plinko\n12. Keno\n13. Wheel\n14. Hi-Lo\n15. Limbo\n\n"
        "Choisis un jeu et tu recevras les prédictions correspondantes ✅"
    )

# Commande /luckyjet réservée à l'admin
async def luckyjet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == admin_id:
        await update.message.reply_text("🎯 Signaux Lucky Jet : Exemple ✅\n15h00 → 2x\n15h07 → 1.5x\n15h16 → 3x")
    else:
        await update.message.reply_text("❌ Accès refusé.")

# Commande /session réservée à l'admin
async def session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != admin_id:
        await update.message.reply_text("❌ Accès refusé.")
        return

    try:
        start_hour = int(context.args[0])   # ex: 7
        end_hour = int(context.args[1])     # ex: 12
        cote = int(context.args[2])         # ex: 2
        valeur = float(context.args[3])     # ex: 1.50
        spacing = int(context.args[4]) if len(context.args) > 4 else 2

        signaux = []
        minute = 0
        while start_hour <= end_hour:
            signaux.append(f"{start_hour:02d}h{minute:02d} → côté {cote} (valeur {valeur})")
            minute += spacing
            if minute >= 60:
                minute = 0
                start_hour += 1

        await update.message.reply_text("📊 Signaux Lucky Jet générés :\n" + "\n".join(signaux))

    except Exception:
        await update.message.reply_text("Usage : /session <start> <end> <cote> <valeur> [espacement]")

# Ajoute les commandes
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("id", id_command))
application.add_handler(CommandHandler("valider", valider))
application.add_handler(CommandHandler("refuser", refuser))
application.add_handler(CommandHandler("jeux", jeux))
application.add_handler(CommandHandler("luckyjet", luckyjet))
application.add_handler(CommandHandler("session", session))

# Routes Flask pour Render - WEBHOOK UNIQUEMENT
@flask_app.route('/')
def index():
    return "Bot en ligne ✅"

@flask_app.route('/webhook', methods=['POST'])
async def webhook():
    """Webhook pour recevoir les mises à jour de Telegram"""
    try:
        # Initialise l'application si nécessaire
        await initialize_app()
        
        # Récupère et traite la mise à jour
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        
        return "OK", 200
    except Exception as e:
        print(f"❌ Erreur webhook: {e}")
        import traceback
        traceback.print_exc()
        return "Error", 500

@flask_app.route('/set_webhook', methods=['POST'])
async def set_webhook():
    """Route pour configurer le webhook"""
    if not WEBHOOK_URL:
        return {"error": "WEBHOOK_URL non configurée"}, 400
    
    try:
        # Initialise l'application avant de configurer le webhook
        await initialize_app()
        await application.bot.set_webhook(url=WEBHOOK_URL)
        print(f"✅ Webhook configuré: {WEBHOOK_URL}")
        return {"status": "Webhook configuré avec succès"}, 200
    except Exception as e:
        print(f"❌ Erreur set_webhook: {e}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    # Lance seulement le serveur Flask (webhook)
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
