import os
import logging
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

logger = logging.getLogger(__name__)

# Keyboard with 4 mood options
keyboard = [
    ["😊 Happy", "😘 Flirty"],
    ["😠 Angry", "😑 Bored"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Global callback for mood updates
mood_callback = None


def set_mood_callback(callback):
    """Set the callback function for mood updates."""
    global mood_callback
    mood_callback = callback


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Startet den Bot und zeigt das Keyboard an."""
    await update.message.reply_text(
        "Hallo! Ich bin ANDI. Wie soll ich mich heute verhalten?",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verarbeitet die Klicks auf das Custom Keyboard."""
    text = update.message.text
    mood = None

    if "😊" in text:
        mood = "happy"
        emoji_response = "😊"
        message = "Modus gewechselt: Ich bin jetzt fröhlich und herzlich! ✨"
    elif "😘" in text:
        mood = "flirty"
        emoji_response = "😘"
        message = "Modus gewechselt: Ich bin jetzt charmant und flirtend! 💋"
    elif "😠" in text:
        mood = "angry"
        emoji_response = "😠"
        message = "Modus gewechselt: Mach dich auf was gefasst! 💀"
    elif "😑" in text:
        mood = "bored"
        emoji_response = "😑"
        message = "Modus gewechselt: Ich bin jetzt gelangweilt... 😏"
    else:
        await update.message.reply_text("Bitte benutze die Tasten unten, um den Modus zu wählen.")
        return

    # Call the mood update callback if set
    if mood_callback:
        mood_callback(mood)
    
    await update.message.reply_text(f"{emoji_response} {message}")
    logger.info(f"Mood changed to: {mood}")


async def start_telegram_bot(callback):
    """Startet den Bot mit mood callback."""
    set_mood_callback(callback)
    
    if not BOT_TOKEN:
        logger.error("TELEGRAM_TOKEN fehlt in der .env – Bot kann nicht gestartet werden")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("ANDI Bot is running... starting polling")
    await application.initialize()
    # Delete webhook to make polling work and drop old pending updates
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.start()
    await application.updater.start_polling()
    # Keep the bot alive to receive updates
    await application.updater.idle()


if __name__ == "__main__":
    # For standalone testing
    logging.basicConfig(level=logging.INFO)
    import asyncio
    asyncio.run(start_telegram_bot(lambda mood: print(f"Mood: {mood}")))