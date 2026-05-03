import time
from telegram_bot import start_bot
from tracker import check_trades
from session import is_active_session, is_new_session, is_close_session
from reporter import daily_report
from config import TELEGRAM_CHAT_ID

from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send(msg):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

def run_tracker_loop():
    while True:

        if is_active_session():
            check_trades(send)

        if is_new_session():
            send("🟢 New session started")

        if is_close_session():
            send("🔴 Session closing")

        time.sleep(15)

def run_report_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler
    import pytz

    scheduler = BackgroundScheduler(timezone="Asia/Jakarta")

    scheduler.add_job(
        lambda: daily_report(send),
        "cron",
        hour=22,
        minute=0
    )

    scheduler.start()

if __name__ == "__main__":
    run_report_scheduler()

    import threading
    threading.Thread(target=run_tracker_loop).start()

    start_bot()
