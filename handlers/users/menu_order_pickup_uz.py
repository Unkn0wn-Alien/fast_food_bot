import asyncpg
import re

from datetime import datetime

from aiogram import types

from loader import dp, db, bot

from config.config import ADMINS

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.dispatcher import FSMContext
from states.menu_pickup_uz import Menu_pickup_uz

from keyboards.default_keyboards.order_button_uz import order_uz
from keyboards.default_keyboards.menu_button_uz import menu_uz
from keyboards.default_keyboards.yes_or_no import yes_or_no_uz
from keyboards.default_keyboards.phone_number import phone_number_uz
from keyboards.default_keyboards.confirm_or_delete import con_or_del_uz
from keyboards.default_keyboards.category_uz import category_button_uz, product_button_uz


@dp.message_handler(text="🏃🏼 Olib ketish", content_types=types.ContentTypes.TEXT)
async def delivery(message: types.Message):
    c_b_u = await category_button_uz()
    await message.answer("Kategoriyani tanlang\n👇👇👇", reply_markup=c_b_u)
    await Menu_pickup_uz.categories.set()


@dp.message_handler(state=Menu_pickup_uz.categories, content_types=types.ContentTypes.TEXT)
async def categories(message: types.Message, state: FSMContext):
    if message.text == "⬅ Ortga":
        await state.finish()
        await message.answer("Buyurtma turini tanlang\n👇👇👇", reply_markup=order_uz)
    else:
        await state.update_data(category=message.text)
        p_b_u = await product_button_uz(message)
        await message.answer("Mahsulot tanlang\n👇👇👇", reply_markup=p_b_u)
        await Menu_pickup_uz.products.set()


@dp.message_handler(state=Menu_pickup_uz.products, content_types=types.ContentTypes.TEXT)
async def products(message: types.Message, state: FSMContext):
    if message.text == "⬅ Ortga":
        c_b_u = await category_button_uz()
        await message.answer("Kategoriyani tanlang\n👇👇👇", reply_markup=c_b_u)
        await Menu_pickup_uz.previous()
    else:
        await state.update_data(product=message.text)
        data = await state.get_data()
        product = data.get("product")
        product_data = await db.get_product_by_id_uz(product_name_uz=product)
        for i in product_data:
            product_id = await db.get_product(i["id"])
            photo = open(f'images/{product_id["photo"]}', "rb")
            await message.answer_photo(photo=photo, caption=f'{product_id["product_name_uz"]}\n\n{product_id["price"]} so\'m', reply_markup=get_keyboard_uz(1))
        await Menu_pickup_uz.product.set()


counter = 1

def get_keyboard_uz(counter):
    ikb = types.InlineKeyboardMarkup(row_width=4)
    button_plus = types.InlineKeyboardButton('➕', callback_data='plus')
    button_soni = types.InlineKeyboardButton(f'{counter} dona', callback_data='1')
    button_minus = types.InlineKeyboardButton('➖', callback_data='minus')
    button_savat_uz = types.InlineKeyboardButton("🛒 Savatga qo'shish", callback_data='savat_uz')
    backuz = types.InlineKeyboardButton("⬅ Ortga", callback_data="backuz")
    ikb.add(button_minus, button_soni, button_plus).add(button_savat_uz).add(backuz)
    return ikb


@dp.callback_query_handler(state=Menu_pickup_uz.product)
async def product_total(callback: types.CallbackQuery, state: FSMContext):
    global counter
    if callback.data == "plus":
        counter += 1
        await bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=get_keyboard_uz(counter))
    elif callback.data == "minus":
        if counter >= 2:
            counter -= 1
            await bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=get_keyboard_uz(counter))
    elif callback.data == "backuz":
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        product_button = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        data = await state.get_data()
        category_name = data.get("category")
        cat_id = await db.get_categories_by_id_uz(category_name_uz=category_name)
        for i in cat_id:
            products = await db.get_products(i["id"])
            for product in products:
                button_text = f'{product["product_name_uz"]}'
                product_button.insert(KeyboardButton(text=button_text))
        product_button.insert("⬅ Ortga")
        await callback.message.answer("Mahsulot tanlang\n👇", reply_markup=product_button)
        await Menu_pickup_uz.products.set()
    elif callback.data == "savat_uz":
        data = await state.get_data()
        product_name = data.get("product")
        product_id = await db.get_product_by_id_uz(product_name_uz=product_name)
        for i in product_id:
            product_data = await db.get_product(i["id"])
            prod_id = product_data["id"]
            price = product_data["price"]
            if_exist = await db.select_cart_if_exist(product_id=prod_id, telegram_id=callback.from_user.id)
            if if_exist is not None:
                await db.delete_cart_if_exist(product_id=prod_id, telegram_id=callback.from_user.id)
            try:
                await db.add_cart(
                    product_id=prod_id,
                    product_name=product_name,
                    price=price,
                    count=int(counter),
                    telegram_id=callback.from_user.id
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=callback.from_user.id)
        counter = 1
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await callback.message.answer("🔄 Yana mahsulot tanlaysizmi?\n👇", reply_markup=yes_or_no_uz)
        await Menu_pickup_uz.yes_or_no.set()


@dp.message_handler(state=Menu_pickup_uz.yes_or_no, content_types=types.ContentTypes.TEXT)
async def yes_or_no(message: types.Message, state: FSMContext):
    await state.update_data(yes_or_no=message.text)
    if message.text == "✅ Ha":
        c_b_u = await category_button_uz()
        await message.answer("Kategoriyani tanlang\n👇👇👇", reply_markup=c_b_u)
        await Menu_pickup_uz.categories.set()
    elif message.text == "❌ Yo'q":
        cart_products = await db.select_cart(telegram_id=message.from_user.id)
        txt = ""
        sum = 0
        for prod_data in cart_products:
            product_name = prod_data["product_name"]
            price = prod_data["price"]
            count = prod_data["count"]
            text = f"Mahsulot nomi: {product_name}\nMahsulot narxi: {price}\nMahsulot soni: {count}\n\n"
            sum += price * count
            txt += text
        txt += f"Umumiy narxi: {sum} so'm"
        await message.answer(txt, reply_markup=con_or_del_uz)
        await Menu_pickup_uz.con_or_del.set()


@dp.message_handler(state=Menu_pickup_uz.con_or_del, content_types=types.ContentTypes.TEXT)
async def con_or_del(message: types.Message, state: FSMContext):
    await state.update_data(con_or_del=message.text)
    if message.text == "🏠 Bosh menyu":
        await state.finish()
        await message.answer("Bosh menyu\n👇👇👇", reply_markup=menu_uz)
    elif message.text == "❌ Bekor qilish":
        await state.finish()
        await db.delete_cart(telegram_id=message.from_user.id)
        await message.answer("Savatdan mahsulotlar o'chirildi\n👇👇👇", reply_markup=menu_uz)
    elif message.text == "✅ Tasdiqlash":
        phone_number = await db.select_phone_number(telegram_id=message.from_user.id)
        await message.answer(f"Buyurtmani ushbu\n{phone_number['phone_number']}\ntelefon raqami bilan bermoqchimisiz?\n👇👇👇", reply_markup=yes_or_no_uz)
        await Menu_pickup_uz.phone_number_order_confirm.set()


@dp.message_handler(state=Menu_pickup_uz.phone_number_order_confirm, content_types=types.ContentTypes.TEXT)
async def new_phone_number_confirm(message: types.Message, state: FSMContext):
    await state.update_data(yes_or_no_phone_number=message.text)
    data = await state.get_data()
    yes_or_no_phone_number = data.get("yes_or_no_phone_number")
    if yes_or_no_phone_number == "❌ Yo'q":
        await message.answer("Yangi telefon raqamni kiriting\nRaqamni (+998xxxxxxxxx yoki 998xxxxxxxxx) shaklida yuboring\n👇👇👇", reply_markup=phone_number_uz)
        await Menu_pickup_uz.new_phone_number.set()
    elif yes_or_no_phone_number == "✅ Ha":
        cart_products = await db.select_cart(telegram_id=message.from_user.id)
        ph_number = await db.select_phone_number(telegram_id=message.from_user.id)
        order_code = datetime.now().strftime('%d%m%Y%H%M%S')
        phone_number = ph_number["phone_number"]
        try:
            await db.add_order(
                order_code=order_code,
                telegram_id=message.from_user.id,
                created_at=datetime.now()
            )
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(telegram_id=message.from_user.id)
        order_id = 0
        order_data = await db.select_order_by_id(telegram_id=message.from_user.id)
        for order_id in order_data:
            order_id = order_id["id"]
        for i in cart_products:
            product_id = i["product_id"]
            count = i["count"]
            product_name = i["product_name"]
            price = i["price"]
            try:
                await db.add_order_details(
                    order_id=order_id,
                    product_id=product_id,
                    count=count,
                    created_at=datetime.now()
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=message.from_user.id)
            try:
                await db.add_order_ontime(
                    product_name=product_name,
                    order_code=order_code,
                    price=price,
                    count=count,
                    telegram_id=message.from_user.id,
                    phone_number=phone_number,
                    product_id=product_id,
                    created_at=datetime.now()
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=message.from_user.id)
        order_products = await db.select_order_ontime(telegram_id=message.from_user.id)
        txt = ""
        txt_admin = ""
        sum = 0
        for order_data in order_products:
            product_name = order_data["product_name"]
            price = order_data["price"]
            count = order_data["count"]
            phone_number = order_data["phone_number"]
            order_code = order_data["order_code"]
            try:
                await db.add_orders_for_user(
                    order_code=order_code,
                    product_name=product_name,
                    price=price,
                    count=count,
                    telegram_id=message.from_user.id,
                    phone_number=phone_number,
                    created_at=datetime.now()
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=message.from_user.id)
            text = f"Mahsulot nomi: {product_name}\nMahsulot narxi: {price}\nMahsulot soni: {count}\n\n"
            text_admin = f"Mahsulot nomi: {product_name}\nMahsulot narxi: {price}\nMahsulot soni: {count}\n\n"
            sum += price * count
            txt += text
            txt_admin += text_admin
        txt += f"Telefon raqamingiz: {phone_number}\nBuyurtma berilgan vaqt: {order_data['created_at']}\nBuyurtma kodi: {order_code}\n\n"
        txt += f"Umumiy narxi: {sum} so'm"
        txt_admin += f"Mijoz telefon raqami: {phone_number}\nBuyurtma berilgan vaqt: {order_data['created_at']}\nBuyurtma kodi: {order_code}\n\n"
        txt_admin += f"Umumiy narxi: {sum} so'm"
        await message.answer(txt)
        await bot.send_message(chat_id=ADMINS[0], text=txt_admin)
        await message.answer("Buyurtmangiz qabul qilindi", reply_markup=menu_uz)
        await db.delete_cart(telegram_id=message.from_user.id)
        await db.delete_order_ontime(telegram_id=message.from_user.id)
        await state.finish()


@dp.message_handler(state=Menu_pickup_uz.new_phone_number, content_types=types.ContentTypes.TEXT)
@dp.message_handler(state=Menu_pickup_uz.new_phone_number, content_types=types.ContentTypes.CONTACT)
async def new_phone_number(message: types.Message, state: FSMContext):
    language = await db.select_language(telegram_id=message.from_user.id)
    match_number = r'''^(\+998|998)(90|91|99|77|94|93|95|97|98|88|33){1}\d{7}$'''
    phone_number = ""
    if message.contact and re.match(match_number, message.contact.phone_number):
        phone_number = message.contact.phone_number
    elif message.text and re.match(match_number, message.text):
        phone_number = message.text
    else:
        if language["language"] == "O'zbek":
            await message.answer("❌ Telefon raqam xato kiritildi\nRaqamni (+998xxxxxxxxx yoki 998xxxxxxxxx) shaklida yuboring\n👇👇👇", reply_markup=phone_number_uz)
            return new_phone_number_confirm
    if phone_number:
        if message.content_type == 'text':
            await state.update_data(new_phone_number=phone_number)
            data = await state.get_data()
            new_phone_number = data.get("new_phone_number")
            await db.update_user_phone_number(phone_number=new_phone_number, telegram_id=message.from_user.id)
            cart_products = await db.select_cart(telegram_id=message.from_user.id)
            ph_number = await db.select_phone_number(telegram_id=message.from_user.id)
            order_code = datetime.now().strftime('%d%m%Y%H%M%S')
            phone_number = ph_number["phone_number"]
            try:
                await db.add_order(
                    order_code=order_code,
                    telegram_id=message.from_user.id,
                    created_at=datetime.now()
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=message.from_user.id)
            order_id = 0
            order_data = await db.select_order_by_id(telegram_id=message.from_user.id)
            for order_id in order_data:
                order_id = order_id["id"]
            for i in cart_products:
                product_id = i["product_id"]
                count = i["count"]
                product_name = i["product_name"]
                price = i["price"]
                try:
                    await db.add_order_details(
                        order_id=order_id,
                        product_id=product_id,
                        count=count,
                        created_at=datetime.now()
                    )
                except asyncpg.exceptions.UniqueViolationError:
                    await db.select_user(telegram_id=message.from_user.id)
                try:
                    await db.add_order_ontime(
                        product_name=product_name,
                        order_code=order_code,
                        price=price,
                        count=count,
                        telegram_id=message.from_user.id,
                        phone_number=phone_number,
                        product_id=product_id,
                        created_at=datetime.now()
                    )
                except asyncpg.exceptions.UniqueViolationError:
                    await db.select_user(telegram_id=message.from_user.id)
            order_products = await db.select_order_ontime(telegram_id=message.from_user.id)
            txt = ""
            txt_admin = ""
            sum = 0
            for order_data in order_products:
                product_name = order_data["product_name"]
                price = order_data["price"]
                count = order_data["count"]
                phone_number = order_data["phone_number"]
                order_code = order_data["order_code"]
                try:
                    await db.add_orders_for_user(
                        order_code=order_code,
                        product_name=product_name,
                        price=price,
                        count=count,
                        telegram_id=message.from_user.id,
                        phone_number=phone_number,
                        created_at=datetime.now()
                    )
                except asyncpg.exceptions.UniqueViolationError:
                    await db.select_user(telegram_id=message.from_user.id)
                text = f"Mahsulot nomi: {product_name}\nMahsulot narxi: {price}\nMahsulot soni: {count}\n\n"
                text_admin = f"Mahsulot nomi: {product_name}\nMahsulot narxi: {price}\nMahsulot soni: {count}\n\n"
                sum += price * count
                txt += text
                txt_admin += text_admin
            txt += f"Telefon raqamingiz: {phone_number}\nBuyurtma berilgan vaqt: {order_data['created_at']}\nBuyurtma kodi: {order_code}\n\n"
            txt += f"Umumiy narxi: {sum} so'm"
            txt_admin += f"Mijoz telefon raqami: {phone_number}\nBuyurtma berilgan vaqt: {order_data['created_at']}\nBuyurtma kodi: {order_code}\n\n"
            txt_admin += f"Umumiy narxi: {sum} so'm"
            await message.answer(txt)
            await bot.send_message(chat_id=ADMINS[0], text=txt_admin)
            await message.answer("Buyurtmangiz qabul qilindi", reply_markup=menu_uz)
            await db.delete_cart(telegram_id=message.from_user.id)
            await db.delete_order_ontime(telegram_id=message.from_user.id)
            await state.finish()
        elif message.content_type == 'contact':
            await state.update_data(new_phone_number=phone_number)
            data = await state.get_data()
            new_phone_number = data.get("new_phone_number")
            await db.update_user_phone_number(phone_number=new_phone_number, telegram_id=message.from_user.id)
            cart_products = await db.select_cart(telegram_id=message.from_user.id)
            ph_number = await db.select_phone_number(telegram_id=message.from_user.id)
            order_code = datetime.now().strftime('%d%m%Y%H%M%S')
            phone_number = ph_number["phone_number"]
            try:
                await db.add_order(
                    order_code=order_code,
                    telegram_id=message.from_user.id,
                    created_at=datetime.now()
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=message.from_user.id)
            order_id = 0
            order_data = await db.select_order_by_id(telegram_id=message.from_user.id)
            for order_id in order_data:
                order_id = order_id["id"]
            for i in cart_products:
                product_id = i["product_id"]
                count = i["count"]
                product_name = i["product_name"]
                price = i["price"]
                try:
                    await db.add_order_details(
                        order_id=order_id,
                        product_id=product_id,
                        count=count,
                        created_at=datetime.now()
                    )
                except asyncpg.exceptions.UniqueViolationError:
                    await db.select_user(telegram_id=message.from_user.id)
                try:
                    await db.add_order_ontime(
                        product_name=product_name,
                        order_code=order_code,
                        price=price,
                        count=count,
                        telegram_id=message.from_user.id,
                        phone_number=phone_number,
                        product_id=product_id,
                        created_at=datetime.now()
                    )
                except asyncpg.exceptions.UniqueViolationError:
                    await db.select_user(telegram_id=message.from_user.id)
            order_products = await db.select_order_ontime(telegram_id=message.from_user.id)
            txt = ""
            txt_admin = ""
            sum = 0
            for order_data in order_products:
                product_name = order_data["product_name"]
                price = order_data["price"]
                count = order_data["count"]
                phone_number = order_data["phone_number"]
                order_code = order_data["order_code"]
                try:
                    await db.add_orders_for_user(
                        order_code=order_code,
                        product_name=product_name,
                        price=price,
                        count=count,
                        telegram_id=message.from_user.id,
                        phone_number=phone_number,
                        created_at=datetime.now()
                    )
                except asyncpg.exceptions.UniqueViolationError:
                    await db.select_user(telegram_id=message.from_user.id)
                text = f"Mahsulot nomi: {product_name}\nMahsulot narxi: {price}\nMahsulot soni: {count}\n\n"
                text_admin = f"Mahsulot nomi: {product_name}\nMahsulot narxi: {price}\nMahsulot soni: {count}\n\n"
                sum += price * count
                txt += text
                txt_admin += text_admin
            txt += f"Telefon raqamingiz: {phone_number}\nBuyurtma berilgan vaqt: {order_data['created_at']}\nBuyurtma kodi: {order_code}\n\n"
            txt += f"Umumiy narxi: {sum} so'm"
            txt_admin += f"Mijoz telefon raqami: {phone_number}\nBuyurtma berilgan vaqt: {order_data['created_at']}\nBuyurtma kodi: {order_code}\n\n"
            txt_admin += f"Umumiy narxi: {sum} so'm"
            await message.answer(txt)
            await bot.send_message(chat_id=ADMINS[0], text=txt_admin)
            await message.answer("Buyurtmangiz qabul qilindi", reply_markup=menu_uz)
            await db.delete_cart(telegram_id=message.from_user.id)
            await db.delete_order_ontime(telegram_id=message.from_user.id)
            await state.finish()