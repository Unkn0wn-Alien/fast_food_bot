from aiogram.dispatcher.filters.state import State, StatesGroup

class Cart_ru(StatesGroup):
    cart_confirm = State()
    type_of_order = State()