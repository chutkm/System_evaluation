import json
from datetime import date, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from bot.states.feedback_states import FeedbackState
from bot.keyboards.rating import rating_keyboard
from bot.keyboards.days import days_keyboard
from bot.config import SCHEDULE_DB_URL
from database.repository import create_feedback
# from analysis_agent.service import process_feedback
from bot.keyboards.main_menu import main_menu

router = Router()

engine = create_async_engine(SCHEDULE_DB_URL)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def check_group_exists(group_name: str) -> bool:
    async with Session() as session:
        result = await session.execute(
            text("SELECT 1 FROM groups WHERE name = :group"),
            {"group": group_name}
        )
        return bool(result.fetchone())


async def get_week_schedule(group_name: str) -> dict:
    """Возвращает пары группы за текущую неделю (текущий день и 3 предыдущих)"""
    today = date.today()
    start_date = today - timedelta(days=3)  # 3 дня до сегодня
    end_date = today

    async with Session() as session:
        result = await session.execute(
            text("""
                SELECT l.date, l.data, g.name as group_name
                FROM lessons l
                JOIN groups g ON g.id = l.group_id
                WHERE g.name = :group
                  AND l.date BETWEEN :start_date AND :end_date
                ORDER BY l.date
            """),
            {"group": group_name, "start_date": start_date, "end_date": end_date}
        )
        rows = result.fetchall()

    schedule = {}
    for row in rows:
        lesson_data = row.data  # словарь

        day_of_week = lesson_data.get("dayOfWeekString", "Неизвестно")
        lesson_data["date"] = row.date  # сохраняем реальную дату пары

        if day_of_week not in schedule:
            schedule[day_of_week] = []

        schedule[day_of_week].append({
            "lesson": lesson_data.get("lessonNumberStart"),
            "discipline": lesson_data.get("discipline"),
            "begin": lesson_data.get("beginLesson"),
            "end": lesson_data.get("endLesson"),
            "auditorium": lesson_data.get("auditorium"),
            "lecturer": lesson_data.get("lecturer"),
            "date": row.date
        })

    return schedule


# -------------------- Handlers -------------------- #

@router.message(F.text == "Оценить обучение")
async def start_feedback(message: Message, state: FSMContext):
    await state.set_state(FeedbackState.group)
    await message.answer("Введите вашу группу:")


@router.message(FeedbackState.group)
async def check_group(message: Message, state: FSMContext):
    group_name = message.text.strip()
    if not await check_group_exists(group_name):
        await message.answer("Группа не найдена. Попробуйте снова.")
        return

    schedule = await get_week_schedule(group_name)
    if not schedule:
        await message.answer("Нет прошедших пар для оценки за текущую неделю.")
        return

    await state.update_data(group_name=group_name, schedule=schedule)
    await state.set_state(FeedbackState.choose_day)
    await message.answer(
        "Выберите день недели:",
        reply_markup=days_keyboard(schedule.keys())
    )


@router.callback_query(F.data.startswith("day_"))
async def choose_day(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[1]
    data = await state.get_data()
    lessons = data["schedule"].get(day, [])

    if not lessons:
        await callback.message.answer("На этот день пар нет.")
        await callback.answer()
        return

    text_lessons = "\n".join(
        f"{l['lesson']}. {l['discipline']} ({l['begin']} - {l['end']}, {l['auditorium']})"
        for l in lessons
    )

    await state.update_data(day=day, lessons=lessons)
    await state.set_state(FeedbackState.choose_lesson)
    await callback.message.answer(f"Пары на {day}:\n{text_lessons}\n\nВведите номер пары:")
    await callback.answer()


@router.message(FeedbackState.choose_lesson)
async def choose_lesson(message: Message, state: FSMContext):
    try:
        lesson_number = int(message.text)
    except ValueError:
        await message.answer("Введите корректный номер пары (число).")
        return

    data = await state.get_data()
    lessons = data.get("lessons", [])
    selected_lesson = next((l for l in lessons if l["lesson"] == lesson_number), None)

    if not selected_lesson:
        await message.answer("Такой пары нет. Попробуйте снова.")
        return

    await state.update_data(
        lesson_number=lesson_number,
        lesson_date=selected_lesson.get("date")
    )

    await state.set_state(FeedbackState.rating)
    await message.answer(
        "Оцените занятие:",
        reply_markup=rating_keyboard()
    )


@router.callback_query(F.data.startswith("rate_"))
async def set_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    await state.update_data(rating=rating)
    await state.set_state(FeedbackState.text)
    await callback.message.answer("Введите отзыв о занятии:")
    await callback.answer()

from datetime import date, datetime, timedelta

@router.message(FeedbackState.text)
async def save_feedback(message: Message, state: FSMContext):
    """Сохранение отзыва с фильтрацией полей для модели Feedback"""
    data = await state.get_data()

    # Фильтруем данные и оставляем только нужные для Feedback
    feedback_data = {
        "group_name": data.get("group_name"),
        "lesson_number": data.get("lesson_number"),
        "lesson_date": data.get("lesson_date"),  # дата пары
        "rating": data.get("rating"),
        "text": message.text
    }

    feedback = await create_feedback(feedback_data)
    # await process_feedback(feedback.id)  # анализ можно раскомментировать позже

    await message.answer("Спасибо за ваш отзыв!")
    await state.clear()


@router.message(F.text == "Главное меню")
async def main_menu_handler(message: Message):
    await message.answer(
        "Система мониторинга удовлетворенности",
        reply_markup=main_menu()
    )