import time
import threading
from app.api_currency import get_rates
from app.api_weather import get_weather
from app.notifier import notify

class BackgroundWorker:
    def __init__(self, interval=600, threshold=0.05):
        self.interval = interval
        self.threshold = threshold
        self.last_rates = None
        self.running = True

    def start(self):
        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()

    def loop(self):
        while self.running:
            try:
                weather = get_weather()
                rates = get_rates()

                print(f"[INFO] Погода: {weather['temp']}°C, Курсы: {rates}")

                if self.last_rates:
                    for code in rates:
                        if abs(rates[code] - self.last_rates[code]) >= self.threshold:
                            notify(
                                f"Изменение курса {code}",
                                f"Новый курс: {rates[code]}"
                            )

                self.last_rates = rates

            except Exception as e:
                print("[ERROR]", e)

            time.sleep(self.interval)
