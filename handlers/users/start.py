import random
import asyncpg
import re

from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db

from states.start_states import FSMFastFood
from states.change_phone_number import ChangePhoneNumber

from keyboards.default_keyboards.language import markup
from keyboards.default_keyboards.phone_number import phone_number_en, phone_number_ru, phone_number_uz
from keyboards.default_keyboards.confirm_code_button_uz import markup_uz
from keyboards.default_keyboards.confirm_code_button_ru import markup_ru
from keyboards.default_keyboards.confirm_code_button_en import markup_en
from keyboards.default_keyboards.menu_button_uz import menu_uz
from keyboards.default_keyboards.menu_button_ru import menu_ru
from keyboards.default_keyboards.menu_button_en import menu_en


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    id = []
    user_ids = await db.select_user_id()
    for user_id in user_ids:
        ids = user_id["telegram_id"]
        id.append(ids)
    if message.from_user.id in id:
        language = await db.select_language(telegram_id=message.from_user.id)
        if language["language"] == "O'zbek":
            await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_uz)
        elif language["language"] == "Русский":
            await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_ru)
        elif language["language"] == "English":
            await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_en)
    else:
        await message.answer("Assalomu aleykum! Botimizga xush kelibsiz!\nIltimos tilni tanlang 👇\n\nЗдравствуйте! Добро пожаловать в наш бот!\nПожалуйста выберите язык 👇\n\nHello! Welcome to our Bot!\nPlease choose the language 👇", reply_markup=markup)
        await FSMFastFood.choose_language.set()


@dp.message_handler(state=FSMFastFood.choose_language, content_types=types.ContentTypes.TEXT)
async def load_language(message: types.Message, state: FSMContext):
    if message.text == "🇺🇿 O'zbek" or message.text == '🇷🇺 Русский' or message.text == '🇬🇧 English':
        await state.update_data(language=message.text)
        data = await state.get_data()
        language = data.get("language")
        lan = language.split(" ")[1]
        if lan == "O'zbek":
            await message.answer("Ro'yxatdan o'tish uchun telefon raqamingizni kiriting.\nRaqamni (+998xxxxxxxxx yoki 998xxxxxxxxx) shaklida yuboring 👇", reply_markup=phone_number_uz)
            await FSMFastFood.phone_number.set()
        elif lan == 'Русский':
            await message.answer("Введите свой номер телефона для регистрации.\nОтправьте номер в виде (+998xxxxxxxxx или 998xxxxxxxxx) 👇", reply_markup=phone_number_ru)
            await FSMFastFood.phone_number.set()
        elif lan == 'English':
            await message.answer("Enter your phone number for register.\nSend number in the form (+998xxxxxxxxx or 998xxxxxxxxx) 👇", reply_markup=phone_number_en)
            await FSMFastFood.phone_number.set()


@dp.message_handler(state=FSMFastFood.phone_number, content_types=types.ContentTypes.TEXT)
@dp.message_handler(state=FSMFastFood.phone_number, content_types=types.ContentTypes.CONTACT)
async def load_contact_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language")
    lan = language.split(" ")[1]
    match_number = r'''^(\+998|998)(90|91|99|77|94|93|95|97|98|88|33){1}\d{7}$'''
    phone_number = ""
    if message.contact and re.match(match_number, message.contact.phone_number):
        phone_number = message.contact.phone_number
    elif message.text and re.match(match_number, message.text):
        phone_number = message.text
    else:
        if lan == "O'zbek":
            await message.answer(
                "❌ Telefon raqam xato kiritildi\nRaqamni (+998xxxxxxxxx yoki 998xxxxxxxxx) shaklida yuboring 👇")
            return load_language
        elif lan == 'Русский':
            await message.answer(
                "❌ Телефон номер неправильно введен\nОтправьте номер в виде (+998xxxxxxxxx или 998xxxxxxxxx) 👇")
            return load_language
        elif lan == 'English':
            await message.answer(
                "❌ Phone number entered incorrectly\nSend the number as (+998xxxxxxxxx или 998xxxxxxxxx) 👇")
            return load_language
    if phone_number:
        if message.content_type == 'text':
            await state.update_data(contact=phone_number)
            if lan == "O'zbek":
                await message.answer("Iltimos F.I.SH ni kiriting 👇")
                await FSMFastFood.full_name.set()
            elif lan == 'Русский':
                await message.answer("Пожалуйста напишите ваше Ф.И.О 👇")
                await FSMFastFood.full_name.set()
            elif lan == 'English':
                await message.answer("Please send your full name 👇")
                await FSMFastFood.full_name.set()
        elif message.content_type == 'contact':
            await state.update_data(contact=phone_number)
            if lan == "O'zbek":
                await message.answer("Iltimos F.I.SH ni kiriting 👇")
                await FSMFastFood.full_name.set()
            elif lan == 'Русский':
                await message.answer("Пожалуйста напишите ваше Ф.И.О 👇")
                await FSMFastFood.full_name.set()
            elif lan == 'English':
                await message.answer("Please send your full name 👇")
                await FSMFastFood.full_name.set()


@dp.message_handler(state=FSMFastFood.full_name, content_types=types.ContentTypes.TEXT)
async def load_fullname(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    data = await state.get_data()
    language = data.get("language")
    lan = language.split(" ")[1]
    phone_number = data.get("contact")
    full_name = data.get("full_name")
    try:
        await db.add_user(
            telegram_id=message.from_user.id,
            language=lan,
            phone_number=phone_number,
            full_name=full_name,
            confirm_code=None,
            created_at=datetime.now()
        )
    except asyncpg.exceptions.UniqueViolationError:
        await db.select_user(telegram_id=message.from_user.id)
    if lan == "O'zbek":
        await message.answer("Telefon raqamga tasdiqlash kodi yuborildi.\nIltimos, kodni kiriting 👇", reply_markup=markup_uz)

        p_n = await db.select_phone_number(telegram_id=message.from_user.id)
        confirm_code = [random.randint(0, 9) for _ in range(6)]
        magic = ''.join(str(i) for i in confirm_code)
        await db.update_confirm_code(confirm_code=magic, phone_number=p_n["phone_number"])
        await message.answer(magic)

    elif lan == 'Русский':
        await message.answer("На номер телефона был отправлен подтвердённый код.\nПожалуйста, введите код 👇", reply_markup=markup_ru)

        p_n = await db.select_phone_number(telegram_id=message.from_user.id)
        confirm_code = [random.randint(0, 9) for _ in range(6)]
        magic = ''.join(str(i) for i in confirm_code)
        await db.update_confirm_code(confirm_code=magic, phone_number=p_n["phone_number"])
        await message.answer(magic)

    elif lan == 'English':
        await message.answer("A confirmation code was sent to the phone number.\nPlease enter the code 👇", reply_markup=markup_en)

        p_n = await db.select_phone_number(telegram_id=message.from_user.id)
        confirm_code = [random.randint(0, 9) for _ in range(6)]
        magic = ''.join(str(i) for i in confirm_code)
        await db.update_confirm_code(confirm_code=magic, phone_number=p_n["phone_number"])
        await message.answer(magic)

    await FSMFastFood.confirm_code.set()


@dp.message_handler(state=FSMFastFood.confirm_code, text="🔄 SMS kodni qayta jo'natish")
@dp.message_handler(state=FSMFastFood.confirm_code, text="🔄 Переотправить СМС код")
@dp.message_handler(state=FSMFastFood.confirm_code, text="🔄 Resend SMS code")
async def send_new_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language")
    lan = language.split(" ")[1]
    if lan == "O'zbek":
        await message.answer("Telefon raqamga yangi tasdiqlash kodi yuborildi.\nIltimos, kodni kiriting 👇",
                            reply_markup=markup_uz)

        p_n = await db.select_phone_number(telegram_id=message.from_user.id)
        confirm_code = [random.randint(0, 9) for _ in range(6)]
        magic = ''.join(str(i) for i in confirm_code)
        await db.update_confirm_code(confirm_code=magic, phone_number=p_n["phone_number"])
        await message.answer(magic)

    elif lan == "Русский":
        await message.answer("На номер телефона был отправлен подтвердённый код.\nПожалуйста, введите код 👇",
                            reply_markup=markup_ru)

        p_n = await db.select_phone_number(telegram_id=message.from_user.id)
        confirm_code = [random.randint(0, 9) for _ in range(6)]
        magic = ''.join(str(i) for i in confirm_code)
        await db.update_confirm_code(confirm_code=magic, phone_number=p_n["phone_number"])
        await message.answer(magic)

    elif lan == "English":
        await message.answer("A confirmation code was sent to the phone number.\nPlease enter the code 👇",
                            reply_markup=markup_en)

        p_n = await db.select_phone_number(telegram_id=message.from_user.id)
        confirm_code = [random.randint(0, 9) for _ in range(6)]
        magic = ''.join(str(i) for i in confirm_code)
        await db.update_confirm_code(confirm_code=magic, phone_number=p_n["phone_number"])
        await message.answer(magic)


@dp.message_handler(state=FSMFastFood.confirm_code, text="📞 Boshqa telefon nomer jo'natish")
@dp.message_handler(state=FSMFastFood.confirm_code, text="📞 Отправить другой телефон номер")
@dp.message_handler(state=FSMFastFood.confirm_code, text="📞 Send another phone number")
async def new_phone_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language")
    lan = language.split(" ")[1]
    if lan == "O'zbek":
        await message.answer("Ro'yxatdan o'tish uchun telefon raqamingizni kiriting.\nRaqamni (+998xxxxxxxxx yoki 998xxxxxxxxx) shaklida yuboring 👇", reply_markup=phone_number_uz)
    elif lan == 'Русский':
        await message.answer("Введите свой номер телефона для регистрации.\nОтправьте номер в виде (+998xxxxxxxxx или 998xxxxxxxxx) 👇", reply_markup=phone_number_ru)
    elif lan == 'English':
        await message.answer("Enter your phone number for register.\nSend number in the form (+998xxxxxxxxx or 998xxxxxxxxx) 👇", reply_markup=phone_number_en)
    await ChangePhoneNumber.new_phone_number.set()


@dp.message_handler(state=ChangePhoneNumber.new_phone_number, content_types=types.ContentTypes.TEXT)
@dp.message_handler(state=ChangePhoneNumber.new_phone_number, content_types=types.ContentTypes.CONTACT)
async def load_contact_number(message: types.Message, state: FSMContext):
    if message.content_type == 'text':
        await state.update_data(new_phone_number=message.text)
    elif message.content_type == 'contact':
        await state.update_data(new_phone_number=message.contact.phone_number)
    data = await state.get_data()
    phone_number = data.get("new_phone_number")
    await db.update_user_phone_number(phone_number=phone_number, telegram_id=message.from_user.id)
    language = await db.select_language(telegram_id=message.from_user.id)
    if language["language"] == "O'zbek":
        await message.answer("Yangi telefon nomerga tasdiqlash kodi yuborildi.\nIltimos, kodni kiriting 👇",
                             reply_markup=markup_uz)

        p_n = await db.select_phone_number(telegram_id=message.from_user.id)
        confirm_code = [random.randint(0, 9) for _ in range(6)]
        magic = ''.join(str(i) for i in confirm_code)
        await db.update_confirm_code(confirm_code=magic, phone_number=p_n["phone_number"])
        await message.answer(magic)

    elif language["language"] == "Русский":
        await message.answer("На новый номер телефона был отправлен подтвердённый код.\nПожалуйста, введите код 👇",
                            reply_markup=markup_ru)

        p_n = await db.select_phone_number(telegram_id=message.from_user.id)
        confirm_code = [random.randint(0, 9) for _ in range(6)]
        magic = ''.join(str(i) for i in confirm_code)
        await db.update_confirm_code(confirm_code=magic, phone_number=p_n["phone_number"])
        await message.answer(magic)

    elif language["language"] == "English":
        await message.answer("A confirmation code was sent to the new phone number.\nPlease enter the code 👇",
                            reply_markup=markup_en)

        p_n = await db.select_phone_number(telegram_id=message.from_user.id)
        confirm_code = [random.randint(0, 9) for _ in range(6)]
        magic = ''.join(str(i) for i in confirm_code)
        await db.update_confirm_code(confirm_code=magic, phone_number=p_n["phone_number"])
        await message.answer(magic)

    await FSMFastFood.confirm_code.set()


@dp.message_handler(state=FSMFastFood.confirm_code, content_types=types.ContentTypes.TEXT)
async def main_menu(message: types.Message, state: FSMContext):
    lan = await db.select_language(telegram_id=message.from_user.id)
    c_c = await db.select_confirm_code(telegram_id=message.from_user.id)
    if message.content_type == 'text':
        if lan["language"] == "O'zbek":
            if message.text == c_c["confirm_code"]:
                await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_uz)
            else:
                await message.answer("Kod noto'g'ri")
                return main_menu
        elif lan["language"] == "Русский":
            if message.text == c_c["confirm_code"]:
                await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_ru)
            else:
                await message.answer("Код неправилный")
                return main_menu
        elif lan["language"] == "English":
            if message.text == c_c["confirm_code"]:
                await message.answer("<a href='https://telegra.ph/Menu-01-11-5'>Menu</a>", reply_markup=menu_en)
            else:
                await message.answer("Invalid code")
                return main_menu
    else:
        return main_menu
    await state.finish()