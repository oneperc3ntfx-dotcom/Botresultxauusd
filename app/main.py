import time
import threading
from datetime import datetime
import pytz

from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    SIGNAL_TOPIC_ID,
    RESULT_TOPIC_ID
)

from market_data import get_price


# =========================
# TIMEZONE
# =========================
TZ = pytz.timezone("Asia/Jakarta")


def now():
    return datetime.now(TZ)


# =========================
# SESSION CONTROL
# =========================
def is_active_session():
    n = now()
    wd = n.weekday()
    h = n.hour
    m = n.minute

    # weekend off
    if wd >= 5:
        return False

    # active 07:00 - 03:50 next day
    if h >= 7 or h < 4:
        if h == 3 and m > 50:
            return False
        return True

    return False


def is_new_session():
    n = now()
    return n.hour == 7 and n.minute == 0


def is_close_session():
    n = now()
    return n.hour == 3 and n.minute == 50


def is_report_time():
    n = now()
    return n.hour == 22 and n.minute == 0


# =========================
# BOT INIT
# =========================
bot = Bot(token=TELEGRAM_BOT_TOKEN)

active_trades = []


# =========================
# SIGNAL PARSER
# =========================
def parse_signal(text):
    try:
        p = text.split()

        return {
            "direction": p[0],
            "pair": p[1],
            "entry": float(p[2]),
            "tp1": float(p[4]),
            "tp2": float(p[6]),
            "sl": float(p[8]),
            "status": "ACTIVE"
        }
    except:
        return None


# =========================
# TELEGRAM SEND
# =========================
def send_result(msg):
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        message_thread_id=RESULT_TOPIC_ID,
        text=msg
    )


def send_signal(msg):
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        message_thread_id=SIGNAL_TOPIC_ID,
        text=msg
    )


# =========================
# TRADE HANDLER
# =========================
def add_trade(trade):
    active_trades.append(trade)


def check_trades():
    price = get_price()

    for trade in active_trades:
        if trade["status"] != "ACTIVE":
            continue

        if trade["direction"] == "BUY":

            if price >= trade["tp2"]:
                trade["status"] = "TP2"
                send_result(f"🎯 TP2 HIT\n{trade}")

            elif price >= trade["tp1"]:
                trade["status"] = "TP1"
                send_result(f"✅ TP1 HIT\n{trade}")

            elif price <= trade["sl"]:
                trade["status"] = "SL"
                send_result(f"❌ SL HIT\n{trade}")

        else:

            if price <= trade["tp2"]:
                trade["status"] = "TP2"
                send_result(f"🎯 TP2 HIT\n{trade}")

            elif price <= trade["tp1"]:
                trade["status"] = "TP1"
                send_result(f"✅ TP1 HIT\n{trade}")

            elif price >= trade["sl"]:
                trade["status"] = "SL"
                send_result(f"❌ SL HIT\n{trade}")


# =========================
# TELEGRAM HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message

    # hanya baca dari SIGNAL TOPIC
    if msg.message_thread_id != SIGNAL_TOPIC_ID:
        return

    if not is_active_session():
        return

    trade = parse_signal(msg.text)

    if trade:
        add_trade(trade)
        send_signal(f"📥 SIGNAL SAVED\n{trade}")


# =========================
# DAILY REPORT
# =========================
def daily_report():
    while True:

        if is_report_time():

            tp1 = len([t for t in active_trades if t["status"] == "TP1"])
            tp2 = len([t for t in active_trades if t["status"] == "TP2"])
            sl = len([t for t in active_trades if t["status"] == "SL"])

            msg = f"""
📊 DAILY REPORT XAUUSD

TP1: {tp1}
TP2: {tp2}
SL: {sl}

Total Trades: {len(active_trades)}
"""

            send_result(msg)

            time.sleep(60)

        time.sleep(10)


# =========================
# SESSION CONTROL LOOP
# =========================
def session_manager():
    global active_trades

    while True:

        if is_new_session():
            active_trades = []
            send_result("🟢 NEW SESSION STARTED")

        if is_close_session():
            send_result("🔴 SESSION CLOSED")

        if is_active_session():
            check_trades()

        time.sleep(15)


# =========================
# START BOT
# =========================
def start_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    app.run_polling()


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    threading.Thread(target=session_manager).start()
    threading.Thread(target=daily_report).start()

    start_bot()
