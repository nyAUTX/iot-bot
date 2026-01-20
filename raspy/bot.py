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


def write_mood(new_mood):
    """Write mood to file for other processes to read."""
    with open("mood.txt", "w") as file:
        file.write(new_mood)
    logger.info(f"Mood written to mood.txt: {new_mood}")


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

    # Write mood to file
    write_mood(mood)
    
    await update.message.reply_text(f"{emoji_response} {message}")
    logger.info(f"Mood changed to: {mood}")


def main():
    """Startet den Bot standalone."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_TOKEN not found in .env file")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("ANDI Bot läuft... (standalone mode)")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()