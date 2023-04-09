from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("🚖 Yetkazib berish")
button_2 = KeyboardButton("🏃🏼 Olib ketish")
button_3 = KeyboardButton("⬅ Ortga")
order_uz = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1, button_2).row(button_3)