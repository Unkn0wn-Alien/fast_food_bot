from aiogram.dispatcher.filters.state import State, StatesGroup

class Menu_pickup_ru(StatesGroup):
    categories = State()
    products = State()
    product = State()
    show_product = State()
    cart = State()
    yes_or_no = State()
    con_or_del = State()
    phone_number_order_confirm = State()
    new_phone_number = State()