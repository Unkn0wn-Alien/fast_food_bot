import asyncpg
import re

from datetime import datetime

from aiogram import types

from loader import dp, db, bot

from config.config import ADMINS

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.dispatcher import FSMContext
from states.menu_en import Menu_en

from keyboards.default_keyboards.order_button_en import order_en
from keyboards.default_keyboards.menu_button_en import menu_en
from keyboards.default_keyboards.yes_or_no import yes_or_no_en
from keyboards.default_keyboards.type_of_pay import ty_of_pay_en
from keyboards.default_keyboards.phone_number import phone_number_en
from keyboards.default_keyboards.location import location_en
from keyboards.default_keyboards.confirm_or_delete import con_or_del_en, confirm_or_delete_order_en
from keyboards.default_keyboards.category_en import category_button_en, product_button_en



@dp.message_handler(text="🛍 Order", content_types=types.ContentTypes.TEXT)
async def menu_order(message: types.Message):
    await message.answer("Choose type of order\n👇👇👇", reply_markup=order_en)


@dp.message_handler(text="🚖 Delivery", content_types=types.ContentTypes.TEXT)
async def delivery(message: types.Message):
    c_b_u = await category_button_en()
    await message.answer("Choose the category\n👇👇👇", reply_markup=c_b_u)
    await Menu_en.categories.set()


@dp.message_handler(state=Menu_en.categories, content_types=types.ContentTypes.TEXT)
async def categories(message: types.Message, state: FSMContext):
    if message.text == "⬅ Back":
        await state.finish()
        await message.answer("Choose type of order\n👇👇👇", reply_markup=order_en)
    else:
        await state.update_data(category=message.text)
        p_b_u = await product_button_en(message)
        await message.answer("Choose product\n👇👇👇", reply_markup=p_b_u)
        await Menu_en.products.set()


@dp.message_handler(state=Menu_en.products, content_types=types.ContentTypes.TEXT)
async def products(message: types.Message, state: FSMContext):
    if message.text == "⬅ Back":
        c_b_u = await category_button_en()
        await message.answer("Choose category\n👇👇👇", reply_markup=c_b_u)
        await Menu_en.previous()
    else:
        await state.update_data(product=message.text)
        data = await state.get_data()
        product = data.get("product")
        product_data = await db.get_product_by_id_en(product_name_en=product)
        for i in product_data:
            product_id = await db.get_product(i["id"])
            photo = open(f'images/{product_id["photo"]}', "rb")
            await message.answer_photo(photo=photo, caption=f'{product_id["product_name_en"]}\n\n{product_id["price"]} sum', reply_markup=get_keyboard_en(1))
        await Menu_en.product.set()


counter = 1

def get_keyboard_en(counter):
    ikb = types.InlineKeyboardMarkup(row_width=4)
    button_pplus = types.InlineKeyboardButton('➕', callback_data='pplus')
    button_ssoni = types.InlineKeyboardButton(f'{counter} qty', callback_data='1')
    button_minnus = types.InlineKeyboardButton('➖', callback_data='minnus')
    button_savat_en = types.InlineKeyboardButton("🛒 Add to basket", callback_data='savat_en')
    backen = types.InlineKeyboardButton("⬅ Back", callback_data="backen")
    ikb.add(button_minnus, button_ssoni, button_pplus).add(button_savat_en).add(backen)
    return ikb


@dp.callback_query_handler(state=Menu_en.product)
async def product_total(callback: types.CallbackQuery, state: FSMContext):
    global counter
    if callback.data == "pplus":
        counter += 1
        await bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=get_keyboard_en(counter))
    elif callback.data == "minnus":
        if counter >= 2:
            counter -= 1
            await bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=get_keyboard_en(counter))
    elif callback.data == "backen":
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        product_button = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        data = await state.get_data()
        category_name = data.get("category")
        cat_id = await db.get_categories_by_id_en(category_name_en=category_name)
        for i in cat_id:
            products = await db.get_products(i["id"])
            for product in products:
                button_text = f'{product["product_name_en"]}'
                product_button.insert(KeyboardButton(text=button_text))
        product_button.insert("⬅ Back")
        await callback.message.answer("Choose product\n👇", reply_markup=product_button)
        await Menu_en.products.set()
    elif callback.data == "savat_en":
        data = await state.get_data()
        product_name = data.get("product")
        product_id = await db.get_product_by_id_en(product_name_en=product_name)
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
        await callback.message.answer("🔄 Is there anything else you want to order?\n👇", reply_markup=yes_or_no_en)
        await Menu_en.yes_or_no.set()


@dp.message_handler(state=Menu_en.yes_or_no, content_types=types.ContentTypes.TEXT)
async def yes_or_no(message: types.Message, state: FSMContext):
    await state.update_data(yes_or_no=message.text)
    if message.text == "✅ Yes":
        c_b_u = await category_button_en()
        await message.answer("Choose category\n👇👇👇", reply_markup=c_b_u)
        await Menu_en.categories.set()
    elif message.text == "❌ No":
        cart_products = await db.select_cart(telegram_id=message.from_user.id)
        txt = ""
        sum = 0
        for prod_data in cart_products:
            product_name = prod_data["product_name"]
            price = prod_data["price"]
            count = prod_data["count"]
            text = f"Name of product: {product_name}\nPrice of product: {price}\nQuantity of product: {count}\n\n"
            sum += price * count
            txt += text
        txt += f"Overall: {sum} sum"
        await message.answer(txt, reply_markup=con_or_del_en)
        await Menu_en.con_or_del.set()


@dp.message_handler(state=Menu_en.con_or_del, content_types=types.ContentTypes.TEXT)
async def con_or_del(message: types.Message, state: FSMContext):
    await state.update_data(con_or_del=message.text)
    if message.text == "🏠 Main menu":
        await state.finish()
        await message.answer("Main menu\n👇👇👇", reply_markup=menu_en)
    elif message.text == "❌ Ignore":
        await state.finish()
        await db.delete_cart(telegram_id=message.from_user.id)
        await message.answer("Products removed from the basket\n👇👇👇", reply_markup=menu_en)
    elif message.text == "✅ Confirm":
        phone_number = await db.select_phone_number(telegram_id=message.from_user.id)
        await message.answer(f"Do you want to give the order with this\n{phone_number['phone_number']}\nphone number?\n👇👇👇", reply_markup=yes_or_no_en)
        await Menu_en.phone_number_order_confirm.set()


@dp.message_handler(state=Menu_en.phone_number_order_confirm, content_types=types.ContentTypes.TEXT)
async def new_phone_number_confirm(message: types.Message, state: FSMContext):
    await state.update_data(yes_or_no_phone_number=message.text)
    data = await state.get_data()
    yes_or_no_phone_number = data.get("yes_or_no_phone_number")
    if yes_or_no_phone_number == "❌ No":
        await message.answer("Send new phone number\nSend the number in the form (+998xxxxxxxxx or 998xxxxxxxxx)\n👇👇👇", reply_markup=phone_number_en)
        await Menu_en.new_phone_number.set()
    elif yes_or_no_phone_number == "✅ Yes":
        await message.answer("Send your address\n👇👇👇", reply_markup=location_en)
        await Menu_en.address.set()


@dp.message_handler(state=Menu_en.new_phone_number, content_types=types.ContentTypes.TEXT)
@dp.message_handler(state=Menu_en.new_phone_number, content_types=types.ContentTypes.CONTACT)
async def new_phone_number(message: types.Message, state: FSMContext):
    language = await db.select_language(telegram_id=message.from_user.id)
    match_number = r'''^(\+998|998)(90|91|99|77|94|93|95|97|98|88|33){1}\d{7}$'''
    phone_number = ""
    if message.contact and re.match(match_number, message.contact.phone_number):
        phone_number = message.contact.phone_number
    elif message.text and re.match(match_number, message.text):
        phone_number = message.text
    else:
        if language["language"] == "English":
            await message.answer("❌ Phone number entered incorrect\nSend the number in the form (+998xxxxxxxxx or 998xxxxxxxxx)\n👇👇👇", reply_markup=phone_number_en)
            return new_phone_number_confirm
    if phone_number:
        if message.content_type == 'text':
            await state.update_data(new_phone_number=phone_number)
            data = await state.get_data()
            new_phone_number = data.get("new_phone_number")
            await db.update_user_phone_number(phone_number=new_phone_number, telegram_id=message.from_user.id)
            await message.answer("Send your address\n👇👇👇", reply_markup=location_en)
            await Menu_en.address.set()
        elif message.content_type == 'contact':
            await state.update_data(new_phone_number=phone_number)
            data = await state.get_data()
            new_phone_number = data.get("new_phone_number")
            await db.update_user_phone_number(phone_number=new_phone_number, telegram_id=message.from_user.id)
            await message.answer("Send your address\n👇👇👇", reply_markup=location_en)
            await Menu_en.address.set()


@dp.message_handler(state=Menu_en.address, content_types=types.ContentTypes.TEXT)
@dp.message_handler(state=Menu_en.address, content_types=types.ContentTypes.LOCATION)
async def load_address(message: types.Message, state: FSMContext):
    if message.content_type == "text":
        await state.update_data(address=message.text)
        data = await state.get_data()
        address = data.get("address")
        cart_products = await db.select_cart(telegram_id=message.from_user.id)
        ph_number = await db.select_phone_number(telegram_id=message.from_user.id)
        phone_number = ph_number["phone_number"]
        try:
            await db.add_address(
                address=address,
                long=None,
                lat=None,
                telegram_id=message.from_user.id,
                created_at=datetime.now()
            )
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(telegram_id=message.from_user.id)
        sum = 0
        txt = ""
        for prod_data in cart_products:
            product_name = prod_data["product_name"]
            price = prod_data["price"]
            count = prod_data["count"]
            text = f"Name of product: {product_name}\nPrice of product: {price}\nQuantity of product: {count}\n\n"
            sum += price * count
            txt += text
        txt += f"Your phone number: {phone_number}\nYour address: {address}\n\n"
        txt += f"Overall: {sum} sum"
        await message.answer(txt, reply_markup=confirm_or_delete_order_en)
        await message.answer("Confirm your phone number and address\n👇👇👇")
        await Menu_en.confirm_order.set()
    if message.content_type == "location":
        await state.update_data(location=message.location)
        data = await state.get_data()
        location = data.get("location")
        try:
            await db.add_address(
                address=None,
                long=str(location["longitude"]),
                lat=str(location["latitude"]),
                telegram_id=message.from_user.id,
                created_at=datetime.now()
            )
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(telegram_id=message.from_user.id)
        await message.answer("Leave your comments on the order and address 👇👇👇\n\nFor example: house, apartment number, landmark, as well as wishes for the order")
        await Menu_en.real_adress.set()


@dp.message_handler(state=Menu_en.real_adress, content_types=types.ContentTypes.ANY)
async def real_feedback(message: types.Message, state: FSMContext):
    if message.content_type != "text":
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    else:
        await state.update_data(order_feedback=message.text)
        data = await state.get_data()
        order_feedback = data.get("order_feedback")
        cart_products = await db.select_cart(telegram_id=message.from_user.id)
        ph_number = await db.select_phone_number(telegram_id=message.from_user.id)
        phone_number = ph_number["phone_number"]
        sum = 0
        txt = ""
        for prod_data in cart_products:
            product_name = prod_data["product_name"]
            price = prod_data["price"]
            count = prod_data["count"]
            text = f"Name of product: {product_name}\nPrice of product: {price}\nQuantity of product: {count}\n\n"
            sum += price * count
            txt += text
        txt += f"Your phone number: {phone_number}\nComment for order: {order_feedback}\n\n"
        txt += f"Overall: {sum} sum"
        await message.answer(txt, reply_markup=confirm_or_delete_order_en)
        await message.answer("Confirm your phone number and address\n👇👇👇")
        await Menu_en.confirm_order.set()


@dp.message_handler(state=Menu_en.confirm_order, content_types=types.ContentTypes.TEXT)
async def confirm_order(message: types.Message, state: FSMContext):
    if message.text == "❌ Ignore":
        await state.finish()
        await db.delete_cart(telegram_id=message.from_user.id)
        await db.delete_address(telegram_id=message.from_user.id)
        await message.answer("Products removed from the basket", reply_markup=menu_en)
    elif message.text == "✅ Confirm":
        await message.answer("Choose the type of payment\n👇👇👇", reply_markup=ty_of_pay_en)
        await Menu_en.type_of_pay.set()


@dp.message_handler(state=Menu_en.type_of_pay, content_types=types.ContentTypes.TEXT)
async def type_of_pay(message: types.Message, state: FSMContext):
    await state.update_data(type_of_pay=message.text)
    data = await state.get_data()
    type_of_pay = data.get("type_of_pay")
    order_feedback = data.get("order_feedback")
    location = data.get("location")
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    order_code = datetime.now().strftime('%d%m%Y%H%M%S')
    address_data = await db.select_address(telegram_id=message.from_user.id)
    ph_number = await db.select_phone_number(telegram_id=message.from_user.id)
    phone_number = ph_number["phone_number"]
    if type_of_pay == "💵 Cash":
        address = ''
        for address in address_data:
            address = address["address"]
        if address is not None:
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
                text = f"Name of product: {product_name}\nPrice of product: {price}\nQuantity of product: {count}\n\n"
                text_admin = f"Name of product: {product_name}\nPrice of product: {price}\nQuantity of product: {count}\n\n"
                sum += price * count
                txt += text
                txt_admin += text_admin
            txt += f"Your phone number: {phone_number}\nYour address: {address}\nTime of order: {order_data['created_at']}\nCode of order: {order_code}\nType of payment: Cash\n\n"
            txt += f"Overall: {sum} sum"
            txt_admin += f"Phone number of customer: {phone_number}\nAddress of customer: {address}\nTime of order: {order_data['created_at']}\nCode of order: {order_code}\nType of payment: Cash\n\n"
            txt_admin += f"Overall: {sum} sum"
            await message.answer(txt)
            await bot.send_message(chat_id=ADMINS[0], text=txt_admin)
            await message.answer("Your order has been accepted\nThey'll be contacting with you soon", reply_markup=menu_en)
            await db.delete_cart(telegram_id=message.from_user.id)
            await db.delete_order_ontime(telegram_id=message.from_user.id)
            await state.finish()
        else:
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
                text = f"Name of product: {product_name}\nPrice of product: {price}\nQuantity of product: {count}\n\n"
                text_admin = f"Name of product: {product_name}\nPrice of product: {price}\nQuantity of product: {count}\n\n"
                sum += price * count
                txt += text
                txt_admin += text_admin
            txt += f"Your phone number: {phone_number}\nTime of order: {order_data['created_at']}\nComment for order: {order_feedback}\nCode of order: {order_code}\nType of payment: Cash\n\n"
            txt += f"Overall: {sum} sum"
            txt_admin += f"Phone number of customer: {phone_number}\nTime of order: {order_data['created_at']}\nComment for order: {order_feedback}\nCode of order: {order_code}\nType of payment: Cash\n\n"
            txt_admin += f"Overall: {sum} sum"
            await message.answer(txt)
            await bot.send_message(chat_id=ADMINS[0], text=txt_admin)
            await bot.send_location(chat_id=ADMINS[0], longitude=location["longitude"], latitude=location["latitude"])
            await message.answer("Your order has been accepted\nThey'll be contacting with you soon", reply_markup=menu_en)
            await db.delete_cart(telegram_id=message.from_user.id)
            await db.delete_order_ontime(telegram_id=message.from_user.id)
            await state.finish()