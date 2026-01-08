import pystray
from PIL import Image, ImageDraw
from app.worker import BackgroundWorker

def create_icon():
    img = Image.new("RGB", (64, 64), "blue")
    d = ImageDraw.Draw(img)
    d.text((20, 20), "$", fill="white")
    return img

def run_tray():
    worker = BackgroundWorker()
    worker.start()

    def on_quit(icon, item):
        worker.running = False
        icon.stop()

    icon = pystray.Icon(
        "CurrencyWeather",
        create_icon(),
        menu=pystray.Menu(
            pystray.MenuItem("Выход", on_quit)
        )
    )

    icon.run()
