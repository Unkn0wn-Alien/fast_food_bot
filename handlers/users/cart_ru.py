from aiogram import types

from aiogram.dispatcher import FSMContext

from loader import dp, db

from states.menu_ru import Menu_ru
from states.menu_pickup_ru import Menu_pickup_ru
from states.cart_ru import Cart_ru


from keyboards.default_keyboards.menu_button_ru import menu_ru
from keyboards.default_keyboards.confirm_or_delete import con_del_back_ru
from keyboards.default_keyboards.order_button_ru import order_ru
from keyboards.default_keyboards.yes_or_no import yes_or_no_ru


@dp.message_handler(text="🛒 Корзина")
async def cart(message: types.Message):
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    if len(cart_products) == 0:
        await message.answer("🤷‍♂️ Корзина пусто", reply_markup=menu_ru)
    else:
        txt = ""
        sum = 0
        for prod_data in cart_products:
            product_name = prod_data["product_name"]
            price = prod_data["price"]
            count = prod_data["count"]
            text = f"Название продукта: {product_name}\nЦена продукта: {price}\nКоличество продукта: {count}\n\n"
            sum += price * count
            txt += text
        txt += f"Общая цена: {sum} сум"
        await message.answer(txt, reply_markup=con_del_back_ru)
        await Cart_ru.cart_confirm.set()


@dp.message_handler(state=Cart_ru.cart_confirm, content_types=types.ContentTypes.TEXT)
async def confirm_cart(message: types.Message, state: FSMContext):
    if message.text == "⬅ Назад":
        await state.finish()
        await message.answer("Главное меню\n👇👇👇", reply_markup=menu_ru)
    elif message.text == "❌ Отказать":
        await state.finish()
        await db.delete_cart(telegram_id=message.from_user.id)
        await message.answer("Товары из корзины удалены\n👇👇👇", reply_markup=menu_ru)
    elif message.text == "✅ Подтверждение":
        await message.answer("Выберите тип заказа\n👇👇👇", reply_markup=order_ru)
        await Cart_ru.type_of_order.set()


@dp.message_handler(state=Cart_ru.type_of_order, content_types=types.ContentTypes.TEXT)
async def delivery(message: types.Message, state: FSMContext):
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    if message.text == "⬅ Назад":
        txt = ""
        sum = 0
        for prod_data in cart_products:
            productname = prod_data["product_name"]
            price = prod_data["price"]
            count = prod_data["count"]
            text = f"Название продукта: {productname}\nЦена продукта: {price}\nКоличество продукта: {count}\n\n"
            sum += price * count
            txt += text
        txt += f"Общая цена: {sum} сум"
        await message.answer(txt, reply_markup=con_del_back_ru)
        await Cart_ru.previous()
    elif message.text == "🚖 Доставка":
        phone_number = await db.select_phone_number(telegram_id=message.from_user.id)
        await message.answer(f"Хотите разместить заказ с этим\n{phone_number['phone_number']}\nномером телефона? 👇", reply_markup=yes_or_no_ru)
        await Menu_ru.phone_number_order_confirm.set()
    elif message.text == "🏃🏼 Самовыноз":
        phone_number = await db.select_phone_number(telegram_id=message.from_user.id)
        await message.answer(f"Хотите разместить заказ с этим\n{phone_number['phone_number']}\nномером телефона? 👇", reply_markup=yes_or_no_ru)
        await Menu_pickup_ru.phone_number_order_confirm.set()