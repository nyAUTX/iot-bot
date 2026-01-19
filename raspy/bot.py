import os
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

keyboard = [["😇 Lieb sein", "😈 Böse sein"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def write_mood(new_mood):
    with open("mood.txt", "w+") as file:
        file.write(new_mood)

## ANDI - TELEGRAM BOT

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Startet den Bot und zeigt das Keyboard an."""
    await update.message.reply_text(
        "Hallo! Ich bin ANDI. Wie soll ich mich heute verhalten?",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verarbeitet die Klicks auf das Custom Keyboard."""
    global current_mode
    text = update.message.text

    if "😇" in text:
        write_mood("good")
        await update.message.reply_text("Modus gewechselt: Ich bin jetzt charmant! ✨")
    elif "😈" in text:
        write_mood("bad")
        await update.message.reply_text("Modus gewechselt: Mach dich auf was gefasst! 💀")
    else:
        await update.message.reply_text("Bitte benutze die Tasten unten, um den Modus zu wählen.")

def main():
    """Startet den Bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ANDI Bot läuft...")
    application.run_polling()

if __name__ == "__main__":
    main()