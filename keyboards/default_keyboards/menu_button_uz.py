from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("🛍 Buyurtma berish")
button_2 = KeyboardButton("✍ Izoh qoldirish")
button_3 = KeyboardButton("⚙ Sozlamalar")
button_4 = KeyboardButton("📋 Mening buyurtmalarim")
button_5 = KeyboardButton("🛒 Savat")
button_6 = KeyboardButton("⬅ Ortga")
menu_uz = ReplyKeyboardMarkup(resize_keyboard=True).row(button_1).row(button_2, button_3).row(button_4, button_5)
back_uz = ReplyKeyboardMarkup(resize_keyboard=True).row(button_6)