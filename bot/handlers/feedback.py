import json
from datetime import date, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from bot.states.feedback_states import FeedbackState
from bot.keyboards.rating import rating_keyboard
from bot.keyboards.days import days_keyboard
from bot.config import SCHEDULE_DB_URL
from database.repository import create_feedback
from bot.keyboards.main_menu import main_menu

router = Router()

engine = create_async_engine(SCHEDULE_DB_URL)
Session = async_sessionmaker(engine, expire_on_commit=False)


# ---------------- UTIL ---------------- #

def format_day_schedule(day_name: str, lessons: list) -> str:
    """Красивый вывод расписания"""
    text = f"= {day_name} ({lessons[0]['date'].strftime('%d.%m')}) =\n\n"

    for l in lessons:
        text += (
            f"-- {l['lesson']} пара {l['begin']} - {l['end']} --\n"
            f"  {l['discipline']}\n"
            f"  Аудитория: {l['auditorium']}\n"
            f"  Преподаватель: {l['lecturer']}\n\n"
        )

    return text


def lessons_keyboard(lessons):
    """Кнопки выбора пары"""
    buttons = []

    for lesson in lessons:
        buttons.append([
            InlineKeyboardButton(
                text=f"{lesson['lesson']} пара",
                callback_data=f"lesson_{lesson['lesson']}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ---------------- DATABASE ---------------- #

async def check_group_exists(group_name: str) -> bool:
    async with Session() as session:
        result = await session.execute(
            text("SELECT 1 FROM groups WHERE name = :group"),
            {"group": group_name}
        )
        return bool(result.fetchone())


async def get_week_schedule(group_name: str) -> dict:
    """Возвращает пары группы за последние 3 дня + сегодня"""
    today = date.today()
    start_date = today - timedelta(days=3)

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
            {
                "group": group_name,
                "start_date": start_date,
                "end_date": today
            }
        )

        rows = result.fetchall()

    schedule = {}

    for row in rows:
        lesson_data = row.data

        day_of_week = lesson_data.get("dayOfWeekString", "Неизвестно")

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


# ---------------- HANDLERS ---------------- #

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
        await message.answer("Нет прошедших пар для оценки.")
        return

    await state.update_data(group_name=group_name, schedule=schedule)

    # показываем расписание
    for day, lessons in schedule.items():
        text_schedule = format_day_schedule(day, lessons)
        await message.answer(text_schedule)

    await state.set_state(FeedbackState.choose_day)

    await message.answer(
        "Выберите день:",
        reply_markup=days_keyboard(schedule.keys())
    )


# ---------------- ВЫБОР ДНЯ ---------------- #

@router.callback_query(F.data.startswith("day_"))
async def choose_day(callback: CallbackQuery, state: FSMContext):

    day = callback.data.split("_")[1]

    data = await state.get_data()
    lessons = data["schedule"].get(day, [])

    if not lessons:
        await callback.message.answer("На этот день пар нет.")
        await callback.answer()
        return

    text_schedule = format_day_schedule(day, lessons)

    await callback.message.answer(text_schedule)

    await state.update_data(day=day, lessons=lessons)

    await state.set_state(FeedbackState.choose_lesson)

    await callback.message.answer(
        "Выберите пару:",
        reply_markup=lessons_keyboard(lessons)
    )

    await callback.answer()


# ---------------- ВЫБОР ПАРЫ ---------------- #

@router.callback_query(F.data.startswith("lesson_"))
async def choose_lesson(callback: CallbackQuery, state: FSMContext):

    lesson_number = int(callback.data.split("_")[1])

    data = await state.get_data()
    lessons = data.get("lessons", [])

    selected_lesson = next(
        (l for l in lessons if l["lesson"] == lesson_number),
        None
    )

    if not selected_lesson:
        await callback.message.answer("Ошибка выбора пары.")
        await callback.answer()
        return

    await state.update_data(
        lesson_number=lesson_number,
        lesson_date=selected_lesson["date"]
    )

    await state.set_state(FeedbackState.rating)

    await callback.message.answer(
        "Оцените занятие:",
        reply_markup=rating_keyboard()
    )

    await callback.answer()


# ---------------- ОЦЕНКА ---------------- #

@router.callback_query(F.data.startswith("rate_"))
async def set_rating(callback: CallbackQuery, state: FSMContext):

    rating = int(callback.data.split("_")[1])

    await state.update_data(rating=rating)

    await state.set_state(FeedbackState.text)

    await callback.message.answer("Введите отзыв о занятии:")

    await callback.answer()


# ---------------- СОХРАНЕНИЕ ---------------- #

@router.message(FeedbackState.text)
async def save_feedback(message: Message, state: FSMContext):

    data = await state.get_data()

    feedback_data = {
        "group_name": data.get("group_name"),
        "lesson_number": data.get("lesson_number"),
        "lesson_date": data.get("lesson_date"),
        "rating": data.get("rating"),
        "text": message.text
    }

    feedback = await create_feedback(feedback_data)

    await message.answer("Спасибо за ваш отзыв!")

    await state.clear()


# ---------------- МЕНЮ ---------------- #

@router.message(F.text == "Главное меню")
async def main_menu_handler(message: Message):
    await message.answer(
        "Система мониторинга удовлетворенности",
        reply_markup=main_menu()
    )

# ---------------- НАЗАД ---------------- #

@router.callback_query(F.data == "back_lesson")
async def back_to_lessons(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    lessons = data.get("lessons", [])

    if not lessons:
        await callback.answer()
        return

    await callback.message.answer(
        "Выберите пару:",
        reply_markup=lessons_keyboard(lessons)
    )

    await state.set_state(FeedbackState.choose_lesson)

    await callback.answer()


# ---------------- В МЕНЮ ---------------- #

@router.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    await callback.message.answer(
        "Главное меню",
        reply_markup=main_menu()
    )

    await callback.answer()