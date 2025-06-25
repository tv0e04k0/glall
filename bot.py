import os
import json
import gspread
import telegram
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Настройки
TG_TOKEN = '7934951805:AAH-Uw-QyYKdU9WMpOa1tAYKiF29X7Z0gIg'
SHEET_ID = '1AbC044-YbcX-USxpdPHt-uL4S9IDeVnCfqWlMZnnJ8k'
SHEET_NAME = 'Остатки'

# Загружаем creds.json из файла
with open('creds.json') as f:
    creds_json = json.load(f)

# Авторизация в Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Инициализация Telegram Bot
bot = telegram.Bot(token=TG_TOKEN)

@app.route('/')
def index():
    return 'Bot is alive!'

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

