import requests


def get_city_coordinates(city: str):
    """
    Получает координаты города через Open-Meteo Geocoding API.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1,
        "language": "ru",
        "format": "json"
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()

        if "results" not in data or not data["results"]:
            print("Город не найден:", city)
            return None

        lat = data["results"][0]["latitude"]
        lon = data["results"][0]["longitude"]

        print(f"Координаты {city}: {lat}, {lon}")
        return lat, lon

    except Exception as e:
        print("Ошибка координат:", e)
        return None


def get_weather(city: str):
    coords = get_city_coordinates(city)

    if coords is None:
        print("Использую Минск по умолчанию")
        lat, lon = 53.9, 27.5667
    else:
        lat, lon = coords

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current_weather=true"
    )

    data = requests.get(url, timeout=5).json()

    return {
        "temp": data["current_weather"]["temperature"],
        "wind": data["current_weather"]["windspeed"],
        "code": data["current_weather"]["weathercode"]
    }
