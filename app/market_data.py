import requests
from config import FINNHUB_API_KEY, FINNHUB_SYMBOL


def get_price():
    url = "https://finnhub.io/api/v1/quote"

    params = {
        "symbol": FINNHUB_SYMBOL,
        "token": FINNHUB_API_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if "c" not in data:
            return 0.0

        return float(data["c"])

    except:
        return 0.0
