from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QDialog, QLineEdit
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
import sys
import datetime

from app.api_weather import get_weather
from app.api_currency import get_rates
from app.settings import load_settings, save_settings


# --- WEATHER ICONS ---
WEATHER_ICONS = {
    0: "☀️",
    1: "🌤",
    2: "⛅",
    3: "☁️",
    45: "🌫",
    48: "🌫",
    51: "🌦",
    61: "🌧",
    71: "❄️",
    80: "🌧",
    95: "⛈"
}


# --- Notification popup ---
class Notification(QWidget):
    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.label = QLabel(text, self)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(50, 50, 50, 220);
                color: white;
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 12px;
            }
        """)
        self.label.adjustSize()
        self.resize(self.label.size())

    def show_with_fade(self, pos):
        self.move(pos)
        self.setWindowOpacity(1)
        self.show()

        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(2000)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.finished.connect(self.close)
        anim.start()
        self._anim = anim


# --- SETTINGS WINDOW ---
class SettingsWindow(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings or {}

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(260, 150)

        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 260, 150)
        self.container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 18px;
                color: white;
                font-family: Segoe UI, sans-serif;
            }
        """)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(12, 12, 12, 0)
        top_bar.addStretch()

        btn_close = QPushButton()
        btn_close.setFixedSize(14, 14)
        btn_close.setStyleSheet("background-color: #555; border-radius: 7px; border: none;")
        btn_close.clicked.connect(self.close)
        top_bar.addWidget(btn_close)

        layout = QVBoxLayout(self.container)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        lbl = QLabel("Город:")
        lbl.setFont(QFont("Segoe UI", 11))

        self.city_input = QLineEdit(self.settings.get("city", "Минск"))
        self.city_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border-radius: 6px;
                padding: 4px 8px;
                border: 1px solid #3a3a3a;
                color: white;
            }
        """)

        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        save_btn.clicked.connect(self.on_save)

        layout.addWidget(lbl)
        layout.addWidget(self.city_input)
        layout.addSpacing(8)
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.drag_pos = QPoint()
        self._anim = None
        self._scale = None

    def on_save(self):
        self.settings["city"] = self.city_input.text().strip() or "Минск"
        save_settings(self.settings)
        self.accept()

    def animate_show(self):
        self.setWindowOpacity(0)
        self.show()

        fade = QPropertyAnimation(self, b"windowOpacity")
        fade.setDuration(250)
        fade.setStartValue(0)
        fade.setEndValue(1)
        fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
        fade.start()
        self._anim = fade

        geo = self.geometry()
        start = geo.adjusted(10, 10, -10, -10)
        scale = QPropertyAnimation(self, b"geometry")
        scale.setDuration(250)
        scale.setStartValue(start)
        scale.setEndValue(geo)
        scale.setEasingCurve(QEasingCurve.Type.OutBack)
        scale.start()
        self._scale = scale

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()


# --- MAIN WINDOW ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()
        self.city = self.settings.get("city", "Минск")
        self.theme = self.settings.get("theme", "dark")
        self.pinned = self.settings.get("pinned", False)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(360, 280)

        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 360, 280)
        self.apply_theme()

        # --- TOP BAR ---
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(12, 12, 12, 0)
        top_bar.setSpacing(8)

        # LEFT: pin, settings, theme
        self.pin_btn = QPushButton("⚪" if not self.pinned else "⚫")
        self.pin_btn.setFixedSize(24, 24)
        self.pin_btn.setStyleSheet("border: none; font-size: 16px;")
        self.pin_btn.setToolTip(
            "Откреплено — окно можно перемещать" if not self.pinned else
            "Закреплено — окно нельзя перемещать"
        )
        self.pin_btn.clicked.connect(self.toggle_pin)
        top_bar.addWidget(self.pin_btn)

        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(24, 24)
        settings_btn.setStyleSheet("border: none; font-size: 16px;")
        settings_btn.clicked.connect(self.open_settings)
        top_bar.addWidget(settings_btn)

        self.theme_btn = QPushButton("🌙" if self.theme == "dark" else "☀️")
        self.theme_btn.setFixedSize(24, 24)
        self.theme_btn.setStyleSheet("border: none; font-size: 16px;")
        self.theme_btn.clicked.connect(self.switch_theme)
        top_bar.addWidget(self.theme_btn)

        top_bar.addStretch()

        # RIGHT: круглые кнопки ⬜ ▭ ✖ (в обратном порядке)
        btn_max = QPushButton()
        btn_max.setFixedSize(14, 14)
        btn_max.setStyleSheet("background-color: #999; border-radius: 7px; border: none;")
        top_bar.addWidget(btn_max)

        btn_min = QPushButton()
        btn_min.setFixedSize(14, 14)
        btn_min.setStyleSheet("background-color: #777; border-radius: 7px; border: none;")
        btn_min.clicked.connect(self.showMinimized)
        top_bar.addWidget(btn_min)

        btn_close = QPushButton()
        btn_close.setFixedSize(14, 14)
        btn_close.setStyleSheet("background-color: #555; border-radius: 7px; border: none;")
        btn_close.clicked.connect(self.close)
        top_bar.addWidget(btn_close)

        # --- WEATHER ---
        self.weather_label = QLabel(f"{self.city}: ...°C")
        self.weather_label.setFont(QFont("Segoe UI", 20))
        self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # --- CURRENCY ---
        self.usd_label = QLabel("USD: ...")
        self.eur_label = QLabel("EUR: ...")
        self.rub_label = QLabel("RUB: ...")

        for lbl in (self.usd_label, self.eur_label, self.rub_label):
            lbl.setFont(QFont("Segoe UI", 14))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setTextFormat(Qt.TextFormat.RichText)

        self.last_update = QLabel("Обновлено: --:--")
        self.last_update.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.last_update.setStyleSheet("color: #bbbbbb; font-size: 12px;")

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: #888;
            }
        """)
        refresh_btn.clicked.connect(self.update_data)

        layout = QVBoxLayout(self.container)
        layout.addLayout(top_bar)
        layout.addSpacing(10)
        layout.addWidget(self.weather_label)
        layout.addWidget(self.usd_label)
        layout.addWidget(self.eur_label)
        layout.addWidget(self.rub_label)
        layout.addWidget(self.last_update)
        layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(600_000)

        self.last_rates = None
        self.update_data()

        self.drag_pos = QPoint()
        self._anim = None
        self._scale = None

    # --- THEMES ---
    def apply_theme(self):
        if self.theme == "dark":
            bg = "#1e1e1e"
            fg = "white"
        else:
            bg = "#ffffff"
            fg = "#222222"

        border = "none" if self.pinned else "1px solid #888888"

        self.container.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                border-radius: 18px;
                border: {border};
                color: {fg};
                font-family: Segoe UI, sans-serif;
            }}
        """)

    def switch_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.settings["theme"] = self.theme
        save_settings(self.settings)
        self.theme_btn.setText("🌙" if self.theme == "dark" else "☀️")
        self.apply_theme()

    # --- PIN ---
    def toggle_pin(self):
        self.pinned = not self.pinned
        self.settings["pinned"] = self.pinned
        save_settings(self.settings)

        if self.pinned:
            self.pin_btn.setText("⚫")
            self.pin_btn.setToolTip("Закреплено — окно нельзя перемещать")
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.show_notification("Окно закреплено")
        else:
            self.pin_btn.setText("⚪")
            self.pin_btn.setToolTip("Откреплено — окно можно перемещать")
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.show_notification("Окно откреплено")

        self.apply_theme()
        self.animate_show()

    # --- NOTIFICATION ---
    def show_notification(self, text):
        notif = Notification(self, text)
        btn_rect = self.pin_btn.geometry()
        btn_pos = self.pin_btn.mapToGlobal(btn_rect.topLeft())
        x = btn_pos.x() + (self.pin_btn.width() - notif.width()) // 2
        y = btn_pos.y() - notif.height() - 10
        notif.show_with_fade(QPoint(x, y))

    # --- SETTINGS ---
    def open_settings(self):
        dlg = SettingsWindow(self, self.settings)
        dlg.move(self.x() + 50, self.y() + 50)
        dlg.animate_show()
        if dlg.exec():
            self.settings = load_settings()
            self.city = self.settings.get("city", "Минск")
            self.update_data()

    # --- DRAG ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.pinned:
            return

        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            self.snap_to_edges()

    # --- SNAP ---
    def snap_to_edges(self):
        x, y = self.x(), self.y()
        w, h = self.width(), self.height()

        screen = QApplication.primaryScreen().geometry()
        sw, sh = screen.width(), screen.height()

        margin = 20

        if abs(x) < margin:
            x = 0
        if abs(y) < margin:
            y = 0
        if abs((sw - (x + w))) < margin:
            x = sw - w
        if abs((sh - (y + h))) < margin:
            y = sh - h

        self.move(x, y)

    # --- ANIMATION ---
    def animate_show(self):
        self.setWindowOpacity(0)
        self.show()

        fade = QPropertyAnimation(self, b"windowOpacity")
        fade.setDuration(250)
        fade.setStartValue(0)
        fade.setEndValue(1)
        fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
        fade.start()
        self._anim = fade

        geo = self.geometry()
        start = geo.adjusted(10, 10, -10, -10)
        scale = QPropertyAnimation(self, b"geometry")
        scale.setDuration(250)
        scale.setStartValue(start)
        scale.setEndValue(geo)
        scale.setEasingCurve(QEasingCurve.Type.OutBack)
        scale.start()
        self._scale = scale

    # --- UPDATE DATA ---
    def update_data(self):
        try:
            weather = get_weather(self.city)
            rates = get_rates()

            icon = WEATHER_ICONS.get(weather.get("code", 0), "🌡")
            self.weather_label.setText(f"{icon}  {self.city}: {weather['temp']}°C")

            def fmt(code, new, old):
                if old is None:
                    return f"{code}: {new}"
                if new > old:
                    return f"{code}: {new} <span style='color:#4caf50;'>▲</span>"
                if new < old:
                    return f"{code}: {new} <span style='color:#f44336;'>▼</span>"
                return f"{code}: {new}"

            if self.last_rates is None:
                self.last_rates = rates

            self.usd_label.setText(fmt("USD", rates["USD"], self.last_rates["USD"]))
            self.eur_label.setText(fmt("EUR", rates["EUR"], self.last_rates["EUR"]))
            self.rub_label.setText(fmt("RUB", rates["RUB"], self.last_rates["RUB"]))

            self.last_rates = rates

            now = datetime.datetime.now().strftime("%H:%M")
            self.last_update.setText(f"Обновлено: {now}")

        except Exception as e:
            self.weather_label.setText("Ошибка обновления")
            print("Ошибка:", e)


def run_window():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.animate_show()
    sys.exit(app.exec())
