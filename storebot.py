import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot

# 1. Bind HTTP port so Render health check passes
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live!")

    def log_message(self, format, *args):
        return

def start_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# 2. Initialize Telegram Bot
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN environment variable is missing on Render!")
else:
    bot = telebot.TeleBot(BOT_TOKEN)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Welcome to the Store Bot!")

    print("Bot polling started successfully.")
    bot.infinity_polling()
