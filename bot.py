import os
import json
import logging
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, MessageHandler, Filters, CommandHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Telegram token и таблица
TOKEN = '7934951805:AAH-Uw-QyYKdU9WMpOa1tAYKiF29X7Z0gIg'
SHEET_ID = '1AbC044-YbcX-USxpdPHt-uL4S9IDeVnCfqWlMZnnJ8k'
SHEET_NAME = 'Остатки'

# Flask сервер
app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)

# Авторизация Google
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS_JSON'])  # из переменной окружения
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Основная логика обработки
def start(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="👋 Привет! Я помогу тебе найти товар на складе.\nВведите часть названия:")

def handle_message(update, context):
    chat_id = update.message.chat_id
    query = update.message.text.lower()

    if not query:
        context.bot.send_message(chat_id=chat_id, text="⚠️ Укажите часть названия.")
        return

    data = sheet.get_all_values()[5:]  # с 6-й строки
    results = []
    for row in data:
        name = row[0].lower()
        total = row[2]
        reserve = row[3]
        available = row[4]
        if query in name and available and available != '0':
            results.append(f"📦 <b>{row[0]}</b>\n— Всего: {total}\n— Резерв: {reserve}\n— Доступно: {available}")

    if results:
        context.bot.send_message(chat_id=chat_id, text="🔎 Найдено:\n\n" + "\n\n".join(results), parse_mode='HTML')
    else:
        context.bot.send_message(chat_id=chat_id, text=f"❌ Ничего не найдено по запросу: \"{query}\"")

# Webhook-обработка
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Keepalive
@app.route('/')
def index():
    return 'Bot is alive!'

# Подключаем Telegram обработчики
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
