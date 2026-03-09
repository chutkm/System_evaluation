from aiogram.fsm.state import State, StatesGroup


class FeedbackState(StatesGroup):

    group = State()

    choose_day = State()

    choose_lesson = State()

    rating = State()

    text = State()