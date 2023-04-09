from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton(text="💵 Naqd")
button_2 = KeyboardButton(text="💵 Наличные")
button_3 = KeyboardButton(text="💵 Cash")
ty_of_pay_uz = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1)
ty_of_pay_ru = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_2)
ty_of_pay_en = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_3)