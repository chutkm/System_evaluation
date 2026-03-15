# # from sqlalchemy import select, func
# # from database.session import AsyncSessionLocal
# # from database.models import Feedback, AggregatedStat

# # async def create_feedback(data: dict):
# #     async with AsyncSessionLocal() as session:
# #         feedback = Feedback(**data)
# #         session.add(feedback)
# #         await session.commit()
# #         await session.refresh(feedback)
# #         return feedback


# # async def update_feedback_analysis(feedback_id, sentiment, topics):
# #     async with AsyncSessionLocal() as session:
# #         result = await session.execute(
# #             select(Feedback).where(Feedback.id == feedback_id)
# #         )
# #         feedback = result.scalar_one()

# #         feedback.sentiment = sentiment
# #         feedback.topics = topics

# #         await session.commit()


# # async def get_all_feedbacks():
# #     async with AsyncSessionLocal() as session:
# #         result = await session.execute(select(Feedback))
# #         return result.scalars().all()


# # async def save_aggregated_stat(data: dict):
# #     async with AsyncSessionLocal() as session:
# #         stat = AggregatedStat(**data)
# #         session.add(stat)
# #         await session.commit()


# from sqlalchemy import select, update, delete, func
# from database.session import AsyncSessionLocal
# from database.models import Feedback, AggregatedStat


# # =========================
# # FEEDBACK CRUD
# # =========================

# async def create_feedback(data: dict) -> Feedback:
#     async with AsyncSessionLocal() as session:
#         feedback = Feedback(**data)
#         session.add(feedback)
#         await session.commit()
#         await session.refresh(feedback)
#         return feedback


# async def get_feedback_by_id(feedback_id: int) -> Feedback | None:
#     async with AsyncSessionLocal() as session:
#         result = await session.execute(
#             select(Feedback).where(Feedback.id == feedback_id)
#         )
#         return result.scalar_one_or_none()


# async def get_all_feedbacks() -> list[Feedback]:
#     async with AsyncSessionLocal() as session:
#         result = await session.execute(select(Feedback))
#         return result.scalars().all()


# async def update_feedback_analysis(
#     feedback_id: int,
#     sentiment: str,
#     topics: str
# ):
#     async with AsyncSessionLocal() as session:
#         await session.execute(
#             update(Feedback)
#             .where(Feedback.id == feedback_id)
#             .values(sentiment=sentiment, topics=topics)
#         )
#         await session.commit()


# # =========================
# # STATISTICS
# # =========================

# async def calculate_average_rating() -> float:
#     async with AsyncSessionLocal() as session:
#         result = await session.execute(
#             select(func.avg(Feedback.rating))
#         )
#         return result.scalar() or 0.0


# async def count_by_sentiment(sentiment: str) -> int:
#     async with AsyncSessionLocal() as session:
#         result = await session.execute(
#             select(func.count())
#             .where(Feedback.sentiment == sentiment)
#         )
#         return result.scalar() or 0


# async def save_aggregated_stat(data: dict):
#     async with AsyncSessionLocal() as session:
#         stat = AggregatedStat(**data)
#         session.add(stat)
#         await session.commit()


import json

from sqlalchemy import select, update

from database.session import AsyncSessionLocal
from database.models import Feedback


# async def create_feedback(data):

#     async with AsyncSessionLocal() as session:

#         feedback = Feedback(**data)

#         session.add(feedback)

#         await session.commit()

#         await session.refresh(feedback)

#         return feedback

async def create_feedback(data):

    async with AsyncSessionLocal() as session:

        teacher_id = await get_or_create_teacher(
            session,
            data["teacher"]
        )

        feedback = Feedback(
            group_name=data["group_name"],
            lesson_number=data["lesson_number"],
            lesson_date=data["lesson_date"],
            rating=data["rating"],
            text=data["text"],
            teacher=teacher_id,
            discipline=data["discipline"]
        )

        session.add(feedback)

        await session.commit()

        return feedback

async def get_feedback_by_id(feedback_id):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )

        return result.scalar_one_or_none()


async def update_feedback_analysis(feedback_id, sentiment, topics):

    async with AsyncSessionLocal() as session:

        await session.execute(
            update(Feedback)
            .where(Feedback.id == feedback_id)
            .values(
                sentiment=sentiment,
                # topics=json.dumps(topics, ensure_ascii=False)
                topics = topics
            )
        )

        await session.commit()


async def get_unprocessed_feedback():
    """
    Получает отзывы, которые еще не анализировались
    """
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Feedback).where(Feedback.sentiment == None)
        )

        feedbacks = result.scalars().all()

        return [
            {
                "id": f.id,
                "text": f.text
            }
            for f in feedbacks
        ]


from sqlalchemy import select
from database.models import Teacher, Feedback


async def get_or_create_teacher(session, teacher_name: str):

    result = await session.execute(
        select(Teacher).where(Teacher.teacher_name == teacher_name)
    )

    teacher = result.scalar_one_or_none()

    if teacher:
        return teacher.id

    new_teacher = Teacher(teacher_name=teacher_name)

    session.add(new_teacher)
    await session.flush()

    return new_teacher.id


from database.models import TeacherRecommendation
from datetime import datetime

async def add_teacher_recommendation(session, teacher_id: int, recommendation: str):
    """
    Создаёт новую запись рекомендации для преподавателя.
    Можно добавлять несколько записей на одного преподавателя.
    """
    rec = TeacherRecommendation(
        teacher_id=teacher_id,
        llm_recommendation=recommendation,
        updated_at=datetime.now()
    )
    session.add(rec)
    await session.commit()
    return rec

async def get_latest_teacher_recommendation(session, teacher_id: int):
    """
    Возвращает последнюю рекомендацию для преподавателя
    """
    result = await session.execute(
        select(TeacherRecommendation)
        .where(TeacherRecommendation.teacher_id == teacher_id)
        .order_by(TeacherRecommendation.updated_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
