import os
import json
import flask
import gspread
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
import telegram
from telegram import ReplyKeyboardMarkup

# === Конфигурация ===
TG_TOKEN = '7934951805:AAH-Uw-QyYKdU9WMpOa1tAYKiF29X7Z0gIg'
SHEET_ID = '1AbC044-YbcX-USxpdPHt-uL4S9IDeVnCfqWlMZnnJ8k'
SHEET_NAME = 'Остатки'

# === Flask-приложение ===
app = Flask(__name__)
bot = telegram.Bot(token=TG_TOKEN)

# === Google Sheets подключение ===
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
with open('creds.json') as f:
    creds_json = json.load(f)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# === Маршрут для Render (проверка) ===
@app.route('/')
def index():
    return 'Bot is alive!'

# === Webhook обработка ===
@app.route('/' + TG_TOKEN, methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    message = update.message
    chat_id = message.chat.id
    text = message.text

    if text == '/start':
        send_main_menu(chat_id)
    elif text == '🔍 Поиск по складу':
        bot.send_message(chat_id, '🔎 Введите часть названия товара:')
    elif text == '🔎 новый поиск':
        bot.send_message(chat_id, '🔎 Введите часть названия товара:')
    elif text == '◀ Назад':
        send_main_menu(chat_id)
    elif text == '❌ отмена':
        bot.send_message(chat_id, '❌ Действие отменено.')
        send_main_menu(chat_id)
    else:
        result = search_stock(text)
        bot.send_message(chat_id, result, reply_markup=get_inline_keyboard())

    return 'ok'

# === Главное меню ===
def send_main_menu(chat_id):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            ['🔍 Поиск по складу'],
            ['🗂 Дополнительный раздел 1'],
            ['📄 Дополнительный раздел 2']
        ],
        resize_keyboard=True
    )
    bot.send_message(chat_id, '👋 Привет! Я помогу тебе. Выбери, что нужно:', reply_markup=keyboard)

# === Клавиатура после поиска ===
def get_inline_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            ['🔎 новый поиск'],
            ['◀ Назад', '❌ отмена']
        ],
        resize_keyboard=True
    )

# === Поиск по таблице ===
def search_stock(query):
    if not query:
        return '⚠️ Укажите часть названия товара.'
    try:
        data = sheet.get_all_values()[5:]  # Считываем с 6 строки
        results = []
        for row in data:
            name = row[0].strip().lower()
            total = row[2] if len(row) > 2 else '0'
            reserve = row[3] if len(row) > 3 else '0'
            available = row[4] if len(row) > 4 else '0'

            if query.lower() in name and available and int(available) > 0:
                results.append(f"📦 {row[0]}\n— Всего: {total}\n— Резерв: {reserve}\n— Доступно: {available}")
        if not results:
            return f'❌ Ничего не найдено по запросу: "{query}"'
        return "🔎 Найдено:\n\n" + "\n\n".join(results[:10])
    except Exception as e:
        return f'❌ Ошибка при поиске: {e}'

# === Запуск сервера (локально) ===
if __name__ == '__main__':
    app.run(port=8080)
