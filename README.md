[README.md](https://github.com/user-attachments/files/24523297/README.md)
# 🌦️ Currency & Weather Desktop App
[RU](#-описание-на-русском) | [EN](#-english-description)

---

## 🇷🇺 Описание на русском

Десктопное приложение на **Python + PyQt6**, которое отображает **погоду в выбранном городе** и **официальные курсы валют НБ РБ** в компактном стильном окне.

### ✨ Возможности

- 🌍 Погода в выбранном городе (Open-Meteo)
- 💱 Курсы валют:
  - USD
  - EUR
  - RUB
- 🔄 Автообновление каждые 10 минут
- 📌 Закрепление окна
- 🌙 Светлая / тёмная тема
- ⚙️ Настройки города
- 🔔 Уведомления об изменении курсов
- 🧲 Прилипание к краям экрана
- 🖥️ Работа через системный трей

### 🧱 Стек технологий

- Python 3.10+
- PyQt6
- requests
- pystray
- Pillow
- plyer

### 🌐 API

- Open-Meteo Weather API
- Open-Meteo Geocoding API
- API НБРБ

### ▶️ Запуск

```bash
pip install -r requirements.txt
python main.py
```

### ⚙️ settings.json

```json
{
    "city": "Минск",
    "theme": "dark",
    "pinned": false
}
```

---

## 🇬🇧 English Description

A desktop application built with **Python + PyQt6** that displays **current weather for a selected city** and **official exchange rates of the National Bank of Belarus**.

### ✨ Features

- 🌍 Weather for any city (Open-Meteo)
- 💱 Currency rates:
  - USD
  - EUR
  - RUB
- 🔄 Automatic updates every 10 minutes
- 📌 Window pin / unpin
- 🌙 Light & Dark themes
- ⚙️ Persistent city settings
- 🔔 Currency change notifications
- 🧲 Screen edge snapping
- 🖥️ System tray support

### 🧱 Tech Stack

- Python 3.10+
- PyQt6
- requests
- pystray
- Pillow
- plyer

### 🌐 APIs Used

- Open-Meteo Weather API
- Open-Meteo Geocoding API
- National Bank of Belarus API

### ▶️ Run

```bash
pip install -r requirements.txt
python main.py
```

### ⚙️ settings.json

```json
{
    "city": "Minsk",
    "theme": "dark",
    "pinned": false
}
```

---

## 📂 Project Structure

```text
currency_weather_service/
│
├── app/
│   ├── api_currency.py     # Курсы валют НБ РБ
│   ├── api_weather.py      # Погода и геокодинг
│   ├── notifier.py         # Системные уведомления
│   ├── settings.py         # Работа с settings.json
│   ├── tray.py             # Иконка в системном трее
│   ├── worker.py           # Фоновый поток
│   ├── ui_window.py        # Главное окно PyQt
│   └── __init__.py
│
├── main.py                 # Точка входа
├── requirements.txt
├── settings.json
└── README.md

