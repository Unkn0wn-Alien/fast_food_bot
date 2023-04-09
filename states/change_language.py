from aiogram.dispatcher.filters.state import State, StatesGroup

class ChangeLanguage(StatesGroup):
    new_language = State()