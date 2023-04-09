from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("✅ Ha")
button_2 = KeyboardButton("✅ Да")
button_3 = KeyboardButton("✅ Yes")
button_4 = KeyboardButton("❌ Yo'q")
button_5 = KeyboardButton("❌ Нет")
button_6 = KeyboardButton("❌ No")
yes_or_no_uz = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1, button_4)
yes_or_no_ru = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_2, button_5)
yes_or_no_en = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_3, button_6)