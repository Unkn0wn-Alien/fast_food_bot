from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("🛍 Заказать")
button_2 = KeyboardButton("✍ Оставить отзыв")
button_3 = KeyboardButton("⚙ Настройки")
button_4 = KeyboardButton("📋 Мои заказы")
button_5 = KeyboardButton("🛒 Корзина")
button_6 = KeyboardButton("⬅ Назад")
menu_ru = ReplyKeyboardMarkup(resize_keyboard=True).row(button_1).row(button_2, button_3).row(button_4, button_5)
back_ru = ReplyKeyboardMarkup(resize_keyboard=True).row(button_6)