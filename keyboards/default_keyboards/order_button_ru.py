from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("🚖 Доставка")
button_2 = KeyboardButton("🏃🏼 Самовыноз")
button_3 = KeyboardButton("⬅ Назад")
order_ru = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1, button_2).row(button_3)