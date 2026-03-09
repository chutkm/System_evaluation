from aiogram.fsm.state import State, StatesGroup

class FeedbackState(StatesGroup):
    group = State()
    week = State()
    date = State()
    lesson = State()
    rating = State()
    text = State()


class ScheduleState(StatesGroup):
    group = State()
    week = State()
    day = State()
    lesson_feedback = State()