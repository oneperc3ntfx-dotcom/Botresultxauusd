def parse_signal(text):
    # FORMAT:
    # BUY XAUUSD 2350 TP1 2355 TP2 2360 SL 2345

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
