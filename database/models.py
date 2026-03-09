from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from database.session import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True)
    group_name = Column(String(100))
    week = Column(Integer)
    date = Column(String(20))
    lesson_number = Column(Integer)

    rating = Column(Integer)
    text = Column(Text)

    sentiment = Column(String(20), nullable=True)
    topics = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AggregatedStat(Base):
    __tablename__ = "aggregated_stats"

    id = Column(Integer, primary_key=True)
    period_type = Column(String(20))  # day/week/month
    period_value = Column(String(50))

    avg_rating = Column(Float)
    positive_count = Column(Integer)
    neutral_count = Column(Integer)
    negative_count = Column(Integer)