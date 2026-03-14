from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Date, Text,JSON


class Base(DeclarativeBase):
    pass


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    group_name = Column(String, nullable=False)
    lesson_number = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    lesson_date = Column(Date, nullable=False)  # эта колонка нужна в БД!
    sentiment = Column(String)
    topics = Column(JSON)

    teacher = Column(String)
    discipline = Column(String)