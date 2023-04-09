from aiogram import types

from aiogram.dispatcher import FSMContext

from loader import dp, db

from states.change_language import ChangeLanguage

from keyboards.default_keyboards.language import mark_up_change_language_uz, markup_uz_lang
from keyboards.default_keyboards.menu_button_uz import menu_uz
from keyboards.default_keyboards.menu_button_ru import menu_ru
from keyboards.default_keyboards.menu_button_en import menu_en


@dp.message_handler(text="⚙ Sozlamalar")
async def settings(message: types.Message):
    await message.answer("Harakatni tanglang 👇", reply_markup=mark_up_change_language_uz)



@dp.message_handler(text="⬅ Ortga")
async def main_menu(message: types.Message):
    await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_uz)


@dp.message_handler(text="🌏 Tilni o'zgartirish")
async def change_language(message: types.Message):
    await message.answer("Tilni tanlang 👇", reply_markup=markup_uz_lang)
    await ChangeLanguage.new_language.set()


@dp.message_handler(state=ChangeLanguage.new_language, text="⬅ Ortga")
async def back_settings(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Harakatni tanglang 👇", reply_markup=mark_up_change_language_uz)


@dp.message_handler(state=ChangeLanguage.new_language, text="🇷🇺 Русский")
async def change_to_russia(message: types.Message, state: FSMContext):
    language = message.text.split(" ")[1]
    await db.update_user_language(language_user=language, telegram_id=message.from_user.id)
    await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_ru)
    await state.finish()


@dp.message_handler(state=ChangeLanguage.new_language, text="🇬🇧 English")
async def change_to_english(message: types.Message, state: FSMContext):
    language = message.text.split(" ")[1]
    await db.update_user_language(language_user=language, telegram_id=message.from_user.id)
    await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_en)
    await state.finish()