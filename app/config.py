import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
SYMBOL = os.getenv("FINNHUB_SYMBOL", "XAUUSD")

TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")
