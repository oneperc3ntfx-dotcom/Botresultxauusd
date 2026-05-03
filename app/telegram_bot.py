from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from signal_parser import parse_signal
from tracker import add_trade
from session import is_active_session

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_active_session():
        return

    text = update.message.text
    trade = parse_signal(text)

    if trade:
        add_trade(trade)
        await update.message.reply_text("📥 Signal recorded")

def start_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
