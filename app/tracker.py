from market_data import get_price

active_trades = []

def add_trade(trade):
    active_trades.append(trade)

def check_trades(send_func):
    price = get_price()

    for trade in active_trades:
        if trade["status"] != "ACTIVE":
            continue

        if trade["direction"] == "BUY":

            if price >= trade["tp2"]:
                trade["status"] = "TP2"
                send_func(f"🎯 TP2 HIT: {trade}")

            elif price >= trade["tp1"]:
                trade["status"] = "TP1"
                send_func(f"✅ TP1 HIT: {trade}")

            elif price <= trade["sl"]:
                trade["status"] = "SL"
                send_func(f"❌ SL HIT: {trade}")

        else:

            if price <= trade["tp2"]:
                trade["status"] = "TP2"
                send_func(f"🎯 TP2 HIT: {trade}")

            elif price <= trade["tp1"]:
                trade["status"] = "TP1"
                send_func(f"✅ TP1 HIT: {trade}")

            elif price >= trade["sl"]:
                trade["status"] = "SL"
                send_func(f"❌ SL HIT: {trade}")
