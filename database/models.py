# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy import Column, Integer, String, Date, Text,JSON
# from sqlalchemy.dialects.postgresql import JSONB


# class Base(DeclarativeBase):
#     pass


# class Feedback(Base):
#     __tablename__ = "feedback"

#     id = Column(Integer, primary_key=True)
#     group_name = Column(String, nullable=False)
#     lesson_number = Column(Integer, nullable=False)
#     rating = Column(Integer, nullable=False)
#     text = Column(Text, nullable=False)
#     lesson_date = Column(Date, nullable=False)  # эта колонка нужна в БД!
#     sentiment = Column(String)
#     topics = Column(JSONB)

#     teacher = Column(String)
#     discipline = Column(String)


from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey,DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

class Base(DeclarativeBase):
    pass


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    teacher_name = Column(String, unique=True, nullable=False)

    feedbacks = relationship("Feedback", back_populates="teacher_rel")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)

    group_name = Column(String, nullable=False)
    lesson_number = Column(Integer, nullable=False)

    rating = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    lesson_date = Column(Date, nullable=False)

    sentiment = Column(String)
    topics = Column(JSONB)

    teacher = Column(Integer, ForeignKey("teachers.id"))
    discipline = Column(String)

    teacher_rel = relationship("Teacher", back_populates="feedbacks")


# class TeacherRecommendation(Base):
#     __tablename__ = "teacher_recommendations"

#     id = Column(Integer, primary_key=True)

#     teacher_id = Column(Integer, ForeignKey("teachers.id"), unique=True)

#     llm_recommendation = Column(Text)

#     updated_at = Column(DateTime, default=datetime.utcnow)

#     teacher = relationship("Teacher")

class TeacherRecommendation(Base):
    __tablename__ = "teacher_recommendations"

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, nullable=False)  # больше нет уникальности
    llm_recommendation = Column(Text)
    updated_at = Column(DateTime)
