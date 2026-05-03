import time
import threading
from datetime import datetime
import pytz

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

    if n.weekday() >= 5:
        return False

    if n.hour >= 7 or n.hour < 4:
        if n.hour == 3 and n.minute > 50:
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
# STORAGE
# =========================
active_trades = []


# =========================
# SAFE SEND (ASYNC CORRECT)
# =========================
async def send(app, msg):
    try:
        await app.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=msg,
            message_thread_id=RESULT_TOPIC_ID
        )
    except Exception as e:
        print("SEND ERROR:", e)


# =========================
# TRADE ENGINE
# =========================
def add_trade(trade):
    active_trades.append(trade)


def check_trades(app):
    price = get_price()

    for t in active_trades:
        if t["status"] != "ACTIVE":
            continue

        if t["direction"] == "BUY":

            if price >= t["tp2"]:
                t["status"] = "TP2"
                threading.Thread(target=lambda: asyncio.run(send(app, f"🎯 TP2 HIT\n{t}"))).start()

            elif price >= t["tp1"]:
                t["status"] = "TP1"
                threading.Thread(target=lambda: asyncio.run(send(app, f"✅ TP1 HIT\n{t}"))).start()

            elif price <= t["sl"]:
                t["status"] = "SL"
                threading.Thread(target=lambda: asyncio.run(send(app, f"❌ SL HIT\n{t}"))).start()

        else:

            if price <= t["tp2"]:
                t["status"] = "TP2"
                threading.Thread(target=lambda: asyncio.run(send(app, f"🎯 TP2 HIT\n{t}"))).start()

            elif price <= t["tp1"]:
                t["status"] = "TP1"
                threading.Thread(target=lambda: asyncio.run(send(app, f"✅ TP1 HIT\n{t}"))).start()

            elif price >= t["sl"]:
                t["status"] = "SL"
                threading.Thread(target=lambda: asyncio.run(send(app, f"❌ SL HIT\n{t}"))).start()


# =========================
# TELEGRAM HANDLER
# =========================
async def handle_message(update: ContextTypes.DEFAULT_TYPE, context):

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
        await send(context.application, f"📥 SIGNAL SAVED\n{trade}")


# =========================
# LOOP THREADS
# =========================
def session_loop(app):
    global active_trades

    while True:

        if is_new_session():
            active_trades = []
            asyncio.run(send(app, "🟢 NEW SESSION STARTED"))

        if is_close_session():
            asyncio.run(send(app, "🔴 SESSION CLOSED"))

        if is_active_session():
            check_trades(app)

        time.sleep(15)


def report_loop(app):
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

            asyncio.run(send(app, msg))
            time.sleep(60)

        time.sleep(10)


# =========================
# START BOT (FIXED)
# =========================
def start_bot():

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # START MESSAGE (ANTI ERROR)
    async def on_start(app):
        await app.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="🤖 BOT AKTIF ✅\nXAUUSD Signal System Running..."
        )

    app.post_init = on_start

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("BOT RUNNING...")

    # THREAD LOOP
    threading.Thread(target=session_loop, args=(app,), daemon=True).start()
    threading.Thread(target=report_loop, args=(app,), daemon=True).start()

    # SAFE POLLING
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message"]
    )


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    start_bot()
