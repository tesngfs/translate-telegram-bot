from aiogram.fsm.state import StatesGroup, State

class OrderFood(StatesGroup):
    choosing_food_name = State()
    answering_user = State()
    admin_text = State()
    admin_text_vop = State()
    answering_usere = State()
    vip_user = State()
    admin_vip = State()
    admin_unvip = State()