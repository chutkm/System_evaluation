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


async def create_feedback(data):

    async with AsyncSessionLocal() as session:

        feedback = Feedback(**data)

        session.add(feedback)

        await session.commit()

        await session.refresh(feedback)

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
                topics=json.dumps(topics, ensure_ascii=False)
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
