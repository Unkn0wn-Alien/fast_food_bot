from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("🚖 Delivery")
button_2 = KeyboardButton("🏃🏼 Pickup")
button_3 = KeyboardButton("⬅ Back")
order_en = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1, button_2).row(button_3)