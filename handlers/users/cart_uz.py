from aiogram import types

from aiogram.dispatcher import FSMContext

from loader import dp, db

from states.menu_uz import Menu_uz
from states.menu_pickup_uz import Menu_pickup_uz
from states.cart_uz import Cart_uz


from keyboards.default_keyboards.menu_button_uz import menu_uz
from keyboards.default_keyboards.confirm_or_delete import con_del_back_uz
from keyboards.default_keyboards.order_button_uz import order_uz
from keyboards.default_keyboards.yes_or_no import yes_or_no_uz


@dp.message_handler(text="🛒 Savat")
async def cart(message: types.Message):
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    if len(cart_products) == 0:
        await message.answer("🤷‍♂️ Savat bo'sh", reply_markup=menu_uz)
    else:
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
        await message.answer(txt, reply_markup=con_del_back_uz)
        await Cart_uz.cart_confirm.set()


@dp.message_handler(state=Cart_uz.cart_confirm, content_types=types.ContentTypes.TEXT)
async def confirm_cart(message: types.Message, state: FSMContext):
    if message.text == "⬅ Ortga":
        await state.finish()
        await message.answer("Bosh menyu\n👇👇👇", reply_markup=menu_uz)
    elif message.text == "❌ Bekor qilish":
        await state.finish()
        await db.delete_cart(telegram_id=message.from_user.id)
        await message.answer("Savatdan mahsulotlar o'chirildi\n👇👇👇", reply_markup=menu_uz)
    elif message.text == "✅ Tasdiqlash":
        await message.answer("Buyurtma turini tanlang\n👇👇👇", reply_markup=order_uz)
        await Cart_uz.type_of_order.set()


@dp.message_handler(state=Cart_uz.type_of_order, content_types=types.ContentTypes.TEXT)
async def delivery(message: types.Message, state: FSMContext):
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    if message.text == "⬅ Ortga":
        txt = ""
        sum = 0
        for prod_data in cart_products:
            productname = prod_data["product_name"]
            price = prod_data["price"]
            count = prod_data["count"]
            text = f"Mahsulot nomi: {productname}\nMahsulot narxi: {price}\nMahsulot soni: {count}\n\n"
            sum += price * count
            txt += text
        txt += f"Umumiy narxi: {sum} so'm"
        await message.answer(txt, reply_markup=con_del_back_uz)
        await Cart_uz.previous()
    elif message.text == "🚖 Yetkazib berish":
        phone_number = await db.select_phone_number(telegram_id=message.from_user.id)
        await message.answer(f"Buyurtmani ushbu\n{phone_number['phone_number']}\ntelefon raqami bilan bermoqchimisiz?\n👇👇👇", reply_markup=yes_or_no_uz)
        await Menu_uz.phone_number_order_confirm.set()
    elif message.text == "🏃🏼 Olib ketish":
        phone_number = await db.select_phone_number(telegram_id=message.from_user.id)
        await message.answer(f"Buyurtmani ushbu\n{phone_number['phone_number']}\ntelefon raqami bilan bermoqchimisiz?\n👇👇👇", reply_markup=yes_or_no_uz)
        await Menu_pickup_uz.phone_number_order_confirm.set()