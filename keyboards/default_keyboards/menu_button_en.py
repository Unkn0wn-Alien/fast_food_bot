from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("🛍 Order")
button_2 = KeyboardButton("✍ Leave review")
button_3 = KeyboardButton("⚙ Settings")
button_4 = KeyboardButton("📋 My orders")
button_5 = KeyboardButton("🛒 Basket")
button_6 = KeyboardButton("⬅ Back")
menu_en = ReplyKeyboardMarkup(resize_keyboard=True).row(button_1).row(button_2, button_3).row(button_4, button_5)
back_en = ReplyKeyboardMarkup(resize_keyboard=True).row(button_6)