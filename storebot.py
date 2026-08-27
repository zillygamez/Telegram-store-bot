import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. Health check server for Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return

def start_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# 2. Telegram Bot Setup
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

PRODUCTS = {
    "p1": {"name": "Wireless Headphones 🎧", "price": "$49.99"},
    "p2": {"name": "Smart Watch ⌚", "price": "$89.99"},
    "p3": {"name": "Gaming Mouse 🖱️", "price": "$29.99"}
}

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛍️ Browse Products", callback_data="catalog"))
    markup.add(InlineKeyboardButton("🛒 My Cart", callback_data="cart"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        f"👋 Hello {message.from_user.first_name}!\n\nWelcome to our store! Choose an option:",
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "catalog":
        markup = InlineKeyboardMarkup()
        for pid, item in PRODUCTS.items():
            markup.add(InlineKeyboardButton(f"{item['name']} - {item['price']}", callback_data=f"item_{pid}"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="main_menu"))
        bot.edit_message_text("🛍️ **Product Catalog**:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("item_"):
        pid = call.data.split("_")[1]
        item = PRODUCTS.get(pid)
        if item:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("➕ Add to Cart", callback_data=f"add_{pid}"))
            markup.add(InlineKeyboardButton("🔙 Back to Catalog", callback_data="catalog"))
            bot.edit_message_text(f"📦 **{item['name']}**\nPrice: {item['price']}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("add_"):
        bot.answer_callback_query(call.id, "Added to cart! 🛒", show_alert=True)

    elif call.data == "cart":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))
        bot.edit_message_text("🛒 Your cart is empty.", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "main_menu":
        bot.edit_message_text("Welcome back! Choose an option:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

bot.infinity_polling()
