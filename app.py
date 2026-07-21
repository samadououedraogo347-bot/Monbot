import os
import asyncio
import sys
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

# Gestion de la boucle d'événements
def get_event_loop():
    """Récupère ou crée une boucle d'événements valide"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Pas de boucle active, on vérifie s'il y en a une fermée
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    
    return loop

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
        # Récupère les arguments
        if len(context.args) < 4:
            await update.message.reply_text(
                "❌ Format incorrect.\n"
                "Usage : /session <start> <end> <cote> <espacement>\n\n"
                "Exemples :\n"
                "/session 7 12 1.50 5\n"
                "/session 10 15 2 3"
            )
            return

        start_hour = int(context.args[0])     # ex: 7
        end_hour = int(context.args[1])       # ex: 12
        cote = float(context.args[2])         # ex: 1.50 ou 2
        espacement = int(context.args[3])     # ex: 5 (en minutes)

        signaux = []
        current_hour = start_hour
        minute = 0

        while current_hour <= end_hour:
            # Formate la cote correctement (1.50 reste 1.50, 2 reste 2)
            if cote == int(cote):
                cote_str = str(int(cote))
            else:
                cote_str = str(cote)
            
            signaux.append(f"{current_hour:02d}h{minute:02d} → {cote_str}x")
            
            minute += espacement
            if minute >= 60:
                minute = minute - 60
                current_hour += 1

        await update.message.reply_text("📊 Signaux Lucky Jet générés :\n" + "\n".join(signaux))

    except ValueError:
        await update.message.reply_text(
            "❌ Erreur dans les valeurs entrées.\n"
            "Assure-toi que :\n"
            "- <start> et <end> sont des nombres entiers\n"
            "- <cote> peut être un nombre décimal (ex: 1.50) ou entier (ex: 2)\n"
            "- <espacement> est un nombre entier en minutes\n\n"
            "Usage : /session <start> <end> <cote> <espacement>"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur : {str(e)}")

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
def webhook():
    """Webhook pour recevoir les mises à jour de Telegram"""
    try:
        # Récupère ou crée une boucle d'événements valide
        loop = get_event_loop()
        
        # Lance la coroutine de traitement du webhook dans la boucle d'événements
        loop.run_until_complete(_process_webhook())
        
        return "OK", 200
    except Exception as e:
        print(f"❌ Erreur webhook: {e}")
        import traceback
        traceback.print_exc()
        return "Error", 500

async def _process_webhook():
    """Traite la mise à jour Telegram de manière asynchrone"""
    try:
        # Initialise l'application si nécessaire
        await initialize_app()
        
        # Récupère et traite la mise à jour
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        
        print("✅ Mise à jour traitée avec succès")
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {e}")
        import traceback
        traceback.print_exc()

@flask_app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Route pour configurer le webhook"""
    if not WEBHOOK_URL:
        return {"error": "WEBHOOK_URL non configurée"}, 400
    
    try:
        # Récupère ou crée une boucle d'événements valide
        loop = get_event_loop()
        
        # Lance la configuration du webhook dans la boucle d'événements
        loop.run_until_complete(_configure_webhook())
        
        return {"status": "Webhook configuré avec succès"}, 200
    except Exception as e:
        print(f"❌ Erreur set_webhook: {e}")
        return {"error": str(e)}, 500

async def _configure_webhook():
    """Configure le webhook de manière asynchrone"""
    try:
        # Initialise l'application avant de configurer le webhook
        await initialize_app()
        await application.bot.set_webhook(url=WEBHOOK_URL)
        print(f"✅ Webhook configuré: {WEBHOOK_URL}")
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        raise

if __name__ == "__main__":
    # Lance seulement le serveur Flask (webhook)
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
