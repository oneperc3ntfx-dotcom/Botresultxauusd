import requests
from config import FINNHUB_API_KEY, SYMBOL

def get_price():
    url = f"https://finnhub.io/api/v1/quote"
    params = {
        "symbol": SYMBOL,
        "token": FINNHUB_API_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    # Finnhub returns:
    # c = current price
    return float(data["c"])
