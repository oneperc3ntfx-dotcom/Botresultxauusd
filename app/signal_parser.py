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
