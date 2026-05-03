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
from signal_parser import parse_signal


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

    if wd >= 5:
        return False

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
# BOT
# =========================
bot = Bot(token=TELEGRAM_BOT_TOKEN)

active_trades = []


# =========================
# SEND MESSAGE
# =========================
def send_result(msg):
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        message_thread_id=RESULT_TOPIC_ID,
        text=msg
    )


# =========================
# TRADE HANDLER
# =========================
def add_trade(trade):
    active_trades.append(trade)


def check_trades():
    price = get_price()

    for t in active_trades:
        if t["status"] != "ACTIVE":
            continue

        if t["direction"] == "BUY":

            if price >= t["tp2"]:
                t["status"] = "TP2"
                send_result(f"🎯 TP2 HIT\n{t}")

            elif price >= t["tp1"]:
                t["status"] = "TP1"
                send_result(f"✅ TP1 HIT\n{t}")

            elif price <= t["sl"]:
                t["status"] = "SL"
                send_result(f"❌ SL HIT\n{t}")

        else:

            if price <= t["tp2"]:
                t["status"] = "TP2"
                send_result(f"🎯 TP2 HIT\n{t}")

            elif price <= t["tp1"]:
                t["status"] = "TP1"
                send_result(f"✅ TP1 HIT\n{t}")

            elif price >= t["sl"]:
                t["status"] = "SL"
                send_result(f"❌ SL HIT\n{t}")


# =========================
# TELEGRAM HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message

    if not msg:
        return

    if SIGNAL_TOPIC_ID and msg.message_thread_id != SIGNAL_TOPIC_ID:
        return

    if not is_active_session():
        return

    trade = parse_signal(msg.text)

    if trade:
        add_trade(trade)
        send_result(f"📥 SIGNAL SAVED\n{trade}")


# =========================
# SESSION LOOP
# =========================
def session_loop():
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
# DAILY REPORT
# =========================
def report_loop():
    while True:

        if is_report_time():

            tp1 = len([x for x in active_trades if x["status"] == "TP1"])
            tp2 = len([x for x in active_trades if x["status"] == "TP2"])
            sl = len([x for x in active_trades if x["status"] == "SL"])

            msg = f"""
📊 DAILY RESULT

TP1: {tp1}
TP2: {tp2}
SL: {sl}

Total: {len(active_trades)}
"""

            send_result(msg)
            time.sleep(60)

        time.sleep(10)


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

    threading.Thread(target=session_loop).start()
    threading.Thread(target=report_loop).start()

    start_bot()
