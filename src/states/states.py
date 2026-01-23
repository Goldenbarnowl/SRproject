from aiogram.fsm.state import State, StatesGroup

class User(StatesGroup):
    wait_time = State()
    menu = State()
    wait_id = State()
