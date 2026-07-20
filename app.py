import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Flask pour Render
flask_app = Flask(__name__)

# Récupère ton token depuis les variables d'environnement Render
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN n'est pas configuré dans les variables d'environnement Render!")

# Crée l'application Telegram
application = Application.builder().token(TOKEN).build()

# ⚠️ Remplace ce nombre par TON vrai ID Telegram
admin_id = 6100143894

# Dictionnaires pour gérer les joueurs
joueurs_attente = {}
joueurs_valides = {}

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

# Routes Flask pour Render
@flask_app.route('/')
def index():
    return "Bot en ligne ✅"

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "OK"

# Point d'entrée principal
if __name__ == "__main__":
    # Mode polling (recommandé pour Render)
    # Le bot va continuellement vérifier les nouveaux messages
    print("🚀 Bot démarré en mode polling...")
    application.run_polling()
