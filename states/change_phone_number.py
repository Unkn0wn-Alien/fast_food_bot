from aiogram.dispatcher.filters.state import State, StatesGroup

class ChangePhoneNumber(StatesGroup):
    new_phone_number = State()