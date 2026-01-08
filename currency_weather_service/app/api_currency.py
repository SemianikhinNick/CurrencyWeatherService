import requests

# ID валют НБ РБ
CURRENCY_IDS = {
    "USD": 431,
    "EUR": 451,
    "RUB": 456
}

def get_rates():
    result = {}
    for code, cid in CURRENCY_IDS.items():
        url = f"https://api.nbrb.by/exrates/rates/{cid}"
        data = requests.get(url, timeout=5).json()
        result[code] = data["Cur_OfficialRate"]
    return result
