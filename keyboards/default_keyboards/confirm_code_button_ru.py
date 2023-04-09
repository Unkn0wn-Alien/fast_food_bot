from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton(text="🔄 Переотправить СМС код")
button_2 = KeyboardButton(text="📞 Отправить другой телефон номер")
markup_ru = ReplyKeyboardMarkup(resize_keyboard=True).row(button_1).row(button_2)