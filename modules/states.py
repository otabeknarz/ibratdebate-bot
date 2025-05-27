from aiogram.fsm.state import StatesGroup, State


class RegistrationState(StatesGroup):
    name = State()
    phone = State()
    english_level = State()
    age = State()
    region = State()
    district = State()
