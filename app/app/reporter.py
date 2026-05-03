from tracker import active_trades
from session import now

def daily_report(send_func):
    tp1 = len([t for t in active_trades if t["status"] == "TP1"])
    tp2 = len([t for t in active_trades if t["status"] == "TP2"])
    sl = len([t for t in active_trades if t["status"] == "SL"])

    msg = f"""
📊 DAILY RESULT XAUUSD

TP1: {tp1}
TP2: {tp2}
SL: {sl}
"""

    send_func(msg)
