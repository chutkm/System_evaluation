# from aiogram import Router, F
# from aiogram.types import Message, CallbackQuery
# from aiogram.fsm.context import FSMContext
# from bot.states.feedback_states import FeedbackState
# from bot.keyboards.rating import rating_keyboard
# from database.repository import create_feedback
# from analysis_agent.service import process_feedback

# router = Router()

# @router.message(F.text == "Оценить обучение")
# async def start_feedback(message: Message, state: FSMContext):
#     await state.set_state(FeedbackState.group)
#     await message.answer("Введите группу:")


# @router.message(FeedbackState.group)
# async def set_week(message: Message, state: FSMContext):
#     await state.update_data(group_name=message.text)
#     await state.set_state(FeedbackState.week)
#     await message.answer("Введите номер недели:")


# @router.message(FeedbackState.week)
# async def set_date(message: Message, state: FSMContext):
#     await state.update_data(week=int(message.text))
#     await state.set_state(FeedbackState.date)
#     await message.answer("Введите дату (YYYY-MM-DD):")


# @router.message(FeedbackState.date)
# async def set_lesson(message: Message, state: FSMContext):
#     await state.update_data(date=message.text)
#     await state.set_state(FeedbackState.lesson)
#     await message.answer("Введите номер пары:")


# @router.message(FeedbackState.lesson)
# async def set_rating(message: Message, state: FSMContext):
#     await state.update_data(lesson_number=int(message.text))
#     await state.set_state(FeedbackState.rating)
#     await message.answer("Оцените занятие:", reply_markup=rating_keyboard())


# @router.callback_query(F.data.startswith("rate_"))
# async def set_text(callback: CallbackQuery, state: FSMContext):
#     rating = int(callback.data.split("_")[1])
#     await state.update_data(rating=rating)
#     await state.set_state(FeedbackState.text)
#     await callback.message.answer("Введите текстовый отзыв:")
#     await callback.answer()


# @router.message(FeedbackState.text)
# async def save_feedback(message: Message, state: FSMContext):
#     data = await state.get_data()
#     data["text"] = message.text

#     feedback = await create_feedback(data)

#     await process_feedback(feedback.id)

#     await message.answer("Спасибо за отзыв!")
#     await state.clear()

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.feedback_states import FeedbackState
from bot.keyboards.rating import rating_keyboard
from database.repository import create_feedback
from analysis_agent.service import process_feedback

router = Router()

# --- Стартовая команда ---
@router.message()
async def start_feedback(message: Message, state: FSMContext):
    if message.text.strip() == "Оценить обучение":
        await state.set_state(FeedbackState.group)
        await message.answer("Введите группу:")

# --- Ввод группы ---
@router.message(FeedbackState.group)
async def set_week(message: Message, state: FSMContext):
    await state.update_data(group_name=message.text.strip())
    await state.set_state(FeedbackState.week)
    await message.answer("Введите номер недели (число):")

# --- Ввод недели ---
@router.message(FeedbackState.week)
async def set_date(message: Message, state: FSMContext):
    try:
        week = int(message.text.strip())
    except ValueError:
        await message.answer("Пожалуйста, введите число для недели.")
        return

    await state.update_data(week=week)
    await state.set_state(FeedbackState.date)
    await message.answer("Введите дату (YYYY-MM-DD):")

# --- Ввод даты ---
@router.message(FeedbackState.date)
async def set_lesson(message: Message, state: FSMContext):
    await state.update_data(date=message.text.strip())
    await state.set_state(FeedbackState.lesson)
    await message.answer("Введите номер пары (число):")

# --- Ввод номера пары ---
@router.message(FeedbackState.lesson)
async def set_rating(message: Message, state: FSMContext):
    try:
        lesson_number = int(message.text.strip())
    except ValueError:
        await message.answer("Пожалуйста, введите число для номера пары.")
        return

    await state.update_data(lesson_number=lesson_number)
    await state.set_state(FeedbackState.rating)
    await message.answer("Оцените занятие (1-5):", reply_markup=rating_keyboard())

# --- Выбор рейтинга через InlineKeyboard ---
@router.callback_query(lambda c: c.data.startswith("rate_"))
async def set_text(callback: CallbackQuery, state: FSMContext):
    try:
        rating = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора рейтинга.")
        return

    await state.update_data(rating=rating)
    await state.set_state(FeedbackState.text)
    await callback.message.answer("Введите текстовый отзыв:")
    await callback.answer()

# --- Ввод текстового отзыва и сохранение ---
@router.message(FeedbackState.text)
async def save_feedback(message: Message, state: FSMContext):
    data = await state.get_data()
    data["text"] = message.text.strip()

    # Сохраняем отзыв в БД
    feedback = await create_feedback(data)

    # Обрабатываем отзыв (sentiment + topics)
    await process_feedback(feedback.id, feedback.text)

    await message.answer("Спасибо за отзыв!")
    await state.clear()