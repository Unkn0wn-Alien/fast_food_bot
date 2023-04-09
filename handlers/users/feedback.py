from datetime import datetime

from aiogram import types

from aiogram.dispatcher import FSMContext

from states.feedback import Feedback

from loader import dp, db

from keyboards.default_keyboards.language import back_uz, back_ru, back_en
from keyboards.default_keyboards.menu_button_uz import menu_uz
from keyboards.default_keyboards.menu_button_ru import menu_ru
from keyboards.default_keyboards.menu_button_en import menu_en


@dp.message_handler(text="✍ Izoh qoldirish")
async def feedback_uz(message: types.Message):
    await message.answer("Fikringizni yozib qoldiring", reply_markup=back_uz)
    await Feedback.feedback.set()


@dp.message_handler(text="✍ Оставить отзыв")
async def feedback_ru(message: types.Message):
    await message.answer("Оставьте ваш отзыв", reply_markup=back_ru)
    await Feedback.feedback.set()


@dp.message_handler(text="✍ Leave review")
async def feedback_uz(message: types.Message):
    await message.answer("✍ Leave your review", reply_markup=back_en)
    await Feedback.feedback.set()


@dp.message_handler(state=Feedback.feedback)
async def back_feedback(message: types.Message, state: FSMContext):
    if message.text == "⬅ Ortga":
        await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_uz)
        await state.finish()
    elif message.text == "⬅ Назадь":
        await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_ru)
        await state.finish()
    elif message.text == "⬅ Back":
        await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_en)
        await state.finish()
    else:
        username = await db.select_username(telegram_id=message.from_user.id)
        await db.add_feedback(full_name=username["full_name"], feedback=message.text, created_at=datetime.now())
        language = await db.select_language(telegram_id=message.from_user.id)
        if language["language"] == "O'zbek":
            await message.answer("Izohingiz uchun rahmat")
            await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_uz)
            await state.finish()
        elif language["language"] == "Русский":
            await message.answer("Спасибо за ваш отзыв")
            await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_ru)
            await state.finish()
        elif language["language"] == "English":
            await message.answer("Thank you four your comment")
            await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_en)
            await state.finish()