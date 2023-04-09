from aiogram import types

from aiogram.dispatcher import FSMContext

from loader import dp, db

from states.menu_en import Menu_en
from states.menu_pickup_en import Menu_pickup_en
from states.cart_en import Cart_en


from keyboards.default_keyboards.menu_button_en import menu_en
from keyboards.default_keyboards.confirm_or_delete import con_del_back_en
from keyboards.default_keyboards.order_button_en import order_en
from keyboards.default_keyboards.yes_or_no import yes_or_no_en


@dp.message_handler(text="🛒 Basket")
async def cart(message: types.Message):
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    if len(cart_products) == 0:
        await message.answer("🤷‍♂️ Basket is empty", reply_markup=menu_en)
    else:
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
        await message.answer(txt, reply_markup=con_del_back_en)
        await Cart_en.cart_confirm.set()


@dp.message_handler(state=Cart_en.cart_confirm, content_types=types.ContentTypes.TEXT)
async def confirm_cart(message: types.Message, state: FSMContext):
    if message.text == "⬅ Back":
        await state.finish()
        await message.answer("Main menu\n👇👇👇", reply_markup=menu_en)
    elif message.text == "❌ Ignore":
        await state.finish()
        await db.delete_cart(telegram_id=message.from_user.id)
        await message.answer("Products removed from the basket\n👇👇👇", reply_markup=menu_en)
    elif message.text == "✅ Confirm":
        await message.answer("Choose type of order\n👇👇👇", reply_markup=order_en)
        await Cart_en.type_of_order.set()


@dp.message_handler(state=Cart_en.type_of_order, content_types=types.ContentTypes.TEXT)
async def delivery(message: types.Message, state: FSMContext):
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    if message.text == "⬅ Back":
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
        await message.answer(txt, reply_markup=con_del_back_en)
        await Cart_en.previous()
    elif message.text == "🚖 Delivery":
        phone_number = await db.select_phone_number(telegram_id=message.from_user.id)
        await message.answer(f"Do you want to give the order with this\n{phone_number['phone_number']}\nphone number?\n👇👇👇", reply_markup=yes_or_no_en)
        await Menu_en.phone_number_order_confirm.set()
    elif message.text == "🏃🏼 Pickup":
        phone_number = await db.select_phone_number(telegram_id=message.from_user.id)
        await message.answer(f"Do you want to give the order with this\n{phone_number['phone_number']}\nphone number?\n👇👇👇", reply_markup=yes_or_no_en)
        await Menu_pickup_en.phone_number_order_confirm.set()