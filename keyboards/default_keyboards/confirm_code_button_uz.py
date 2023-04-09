from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton(text="🔄 SMS kodni qayta jo'natish")
button_2 = KeyboardButton(text="📞 Boshqa telefon nomer jo'natish")
markup_uz = ReplyKeyboardMarkup(resize_keyboard=True).row(button_1).row(button_2)