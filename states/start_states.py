from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMFastFood(StatesGroup):
    choose_language = State()
    phone_number = State()
    full_name = State()
    confirm_code = State()