import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
FINNHUB_SYMBOL = os.getenv("FINNHUB_SYMBOL", "XAUUSD")

TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")

# TOPIC IDS
SIGNAL_TOPIC_ID = int(os.getenv("SIGNAL_TOPIC_ID", "0"))
RESULT_TOPIC_ID = int(os.getenv("RESULT_TOPIC_ID", "0"))
