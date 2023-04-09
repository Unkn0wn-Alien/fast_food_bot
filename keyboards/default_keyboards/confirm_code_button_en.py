from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton(text="🔄 Resend SMS code")
button_2 = KeyboardButton(text="📞 Send another phone number")
markup_en = ReplyKeyboardMarkup(resize_keyboard=True).row(button_1).row(button_2)