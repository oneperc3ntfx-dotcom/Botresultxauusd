import os

# =========================
# TELEGRAM
# =========================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
if TELEGRAM_CHAT_ID:
    TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID)

# =========================
# FINNHUB
# =========================
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
FINNHUB_SYMBOL = os.getenv("FINNHUB_SYMBOL", "OANDA:XAU_USD")

# =========================
# TIMEZONE
# =========================
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")

# =========================
# TOPICS
# =========================
SIGNAL_TOPIC_ID = os.getenv("SIGNAL_TOPIC_ID")
RESULT_TOPIC_ID = os.getenv("RESULT_TOPIC_ID")

if SIGNAL_TOPIC_ID:
    SIGNAL_TOPIC_ID = int(SIGNAL_TOPIC_ID)

if RESULT_TOPIC_ID:
    RESULT_TOPIC_ID = int(RESULT_TOPIC_ID)
