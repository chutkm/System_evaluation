import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy import Integer, String, Text, Date
import os
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "SCHEDULE_DB_URL"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)

class Lesson(Base):
    __tablename__ = "lessons"
    id = mapped_column(Integer, primary_key=True)
    group_id = mapped_column(Integer)
    date = mapped_column(Date)
    data = mapped_column(Text)

async def check_group(name: str) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Group).where(Group.name == name))
        return result.scalar_one_or_none() is not None

async def get_week_schedule(group_name: str, week_start: date):
    """Возвращает расписание с понедельника по воскресенье."""
    async with AsyncSessionLocal() as session:
        # Сначала получаем id группы
        result = await session.execute(select(Group).where(Group.name == group_name))
        group = result.scalar_one_or_none()
        if not group:
            return None
        
        week_end = week_start + timedelta(days=6)
        result = await session.execute(
            select(Lesson).where(
                Lesson.group_id == group.id,
                Lesson.date >= week_start,
                Lesson.date <= week_end
            ).order_by(Lesson.date)
        )
        lessons = result.scalars().all()
        return lessons

def parse_lesson_data(lesson):
    """Возвращает json словарь из lesson.data"""
    return json.loads(lesson.data)