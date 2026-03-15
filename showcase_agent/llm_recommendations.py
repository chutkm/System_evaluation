# # def generate_recommendations(metrics):

# #     recommendations = []

# #     if metrics["avg_rating"] < 3.5:
# #         recommendations.append(
# #             "Низкая средняя оценка дисциплин. Рекомендуется провести аудит качества преподавания."
# #         )

# #     if metrics["negative_share"] > 0.3:
# #         recommendations.append(
# #             "Высокая доля негативных отзывов. Необходимо выявить проблемные дисциплины."
# #         )

# #     return recommendations

# def generate_recommendations(metrics):

#     recommendations = []

#     avg_rating = metrics.get("avg_rating", 0)
#     negative_share = metrics.get("negative_share", 0)

#     # --- оценка средней оценки ---
#     if avg_rating >= 4.5:
#         recommendations.append(
#             "Очень высокий уровень удовлетворенности студентов. Рекомендуется сохранить текущие методы преподавания и распространить лучшие практики."
#         )

#     elif 4.0 <= avg_rating < 4.5:
#         recommendations.append(
#             "Хороший уровень преподавания. Можно дополнительно развивать интерактивные методы обучения и практические задания."
#         )

#     elif 3.5 <= avg_rating < 4.0:
#         recommendations.append(
#             "Средний уровень удовлетворенности. Рекомендуется проанализировать темы с наибольшим количеством замечаний студентов."
#         )

#     elif 3.0 <= avg_rating < 3.5:
#         recommendations.append(
#             "Низкая средняя оценка дисциплины. Желательно пересмотреть формат проведения занятий и нагрузку студентов."
#         )

#     else:
#         recommendations.append(
#             "Критически низкая средняя оценка. Рекомендуется провести аудит качества преподавания и методических материалов."
#         )

#     # --- анализ доли негативных отзывов ---
#     if negative_share == 0:
#         recommendations.append(
#             "Негативных отзывов не обнаружено. Ваши студенты довольны — благодарим за качественную работу!"
#         )

#     elif 0 < negative_share <= 0.1:
#         recommendations.append(
#             "Очень низкая доля негативных отзывов. Текущий уровень преподавания оценивается студентами положительно."
#         )

#     elif 0.1 < negative_share <= 0.3:
#         recommendations.append(
#             "Наблюдается умеренное количество негативных отзывов. Рекомендуется проанализировать отдельные проблемные темы."
#         )

#     elif 0.3 < negative_share <= 0.5:
#         recommendations.append(
#             "Высокая доля негативных отзывов. Необходимо выявить проблемные дисциплины и провести корректирующие меры."
#         )

#     else:
#         recommendations.append(
#             "Критически высокая доля негативных отзывов. Требуется срочный анализ качества преподавания и обратной связи от студентов."
#         )

#     return recommendations



# from sqlalchemy import text
# from sqlalchemy import create_engine
# from bot.config import DATABASE_SYNC_URL

# # подключение к БД
# engine = create_engine(DATABASE_SYNC_URL)


# # --------------------------------------------------
# # Генерация рекомендаций (заглушка вместо LLM)
# # --------------------------------------------------

# def generate_recommendations(metrics):

#     recommendations = []

#     avg_rating = metrics.get("avg_rating", 0)
#     negative_share = metrics.get("negative_share", 0)

#     # --- анализ средней оценки ---
#     if avg_rating >= 4.5:
#         recommendations.append(
#             "Очень высокий уровень удовлетворенности студентов. Рекомендуется сохранить текущие методы преподавания."
#         )

#     elif 4.0 <= avg_rating < 4.5:
#         recommendations.append(
#             "Хороший уровень преподавания. Можно дополнительно развивать интерактивные методы обучения."
#         )

#     elif 3.5 <= avg_rating < 4.0:
#         recommendations.append(
#             "Средний уровень удовлетворенности. Рекомендуется проанализировать проблемные темы."
#         )

#     elif 3.0 <= avg_rating < 3.5:
#         recommendations.append(
#             "Низкая средняя оценка дисциплины. Желательно пересмотреть формат проведения занятий."
#         )

#     else:
#         recommendations.append(
#             "Критически низкая средняя оценка. Рекомендуется провести аудит качества преподавания."
#         )

#     # --- анализ негативных отзывов ---
#     if negative_share == 0:
#         recommendations.append(
#             "Негативных отзывов не обнаружено. Студенты довольны качеством обучения."
#         )

#     elif 0 < negative_share <= 0.1:
#         recommendations.append(
#             "Очень низкая доля негативных отзывов."
#         )

#     elif 0.1 < negative_share <= 0.3:
#         recommendations.append(
#             "Наблюдается умеренное количество негативных отзывов. Рекомендуется анализ отдельных проблемных тем."
#         )

#     elif 0.3 < negative_share <= 0.5:
#         recommendations.append(
#             "Высокая доля негативных отзывов. Необходимо провести корректирующие меры."
#         )

#     else:
#         recommendations.append(
#             "Критически высокая доля негативных отзывов. Требуется срочный анализ преподавания."
#         )

#     return recommendations


# # --------------------------------------------------
# # Получение метрик преподавателя
# # --------------------------------------------------

# def get_teacher_metrics(teacher_id):

#     with engine.connect() as conn:

#         result = conn.execute(
#             text("""
#             SELECT
#                 AVG(rating) as avg_rating,
#                 AVG(
#                     CASE
#                         WHEN sentiment = 'negative' THEN 1
#                         ELSE 0
#                     END
#                 ) as negative_share
#             FROM feedback
#             WHERE teacher = :teacher_id
#             """),
#             {"teacher_id": teacher_id}
#         ).fetchone()

#         return {
#             "avg_rating": result.avg_rating or 0,
#             "negative_share": result.negative_share or 0
#         }


# # --------------------------------------------------
# # Проверка есть ли рекомендация в БД
# # --------------------------------------------------

# def get_saved_recommendation(teacher_id):

#     with engine.connect() as conn:

#         result = conn.execute(
#             text("""
#             SELECT llm_recommendation
#             FROM teacher_recommendations
#             WHERE teacher_id = :teacher_id
#             """),
#             {"teacher_id": teacher_id}
#         ).fetchone()

#         if result:
#             return result[0]

#         return None


# # --------------------------------------------------
# # Сохранение рекомендации
# # --------------------------------------------------

# # def save_recommendation(teacher_id, recommendation):

# #     with engine.begin() as conn:

# #         conn.execute(
# #             text("""
# #             INSERT INTO teacher_recommendations
# #             (teacher_id, llm_recommendation)
# #             VALUES (:teacher_id, :rec)
# #             """),
# #             {
# #                 "teacher_id": teacher_id,
# #                 "rec": recommendation
# #             }
# #         )
# from datetime import datetime
# from sqlalchemy.ext.asyncio import AsyncSession
# from database.models import TeacherRecommendation

# async def save_teacher_recommendation(session: AsyncSession, teacher_id: int, recommendation: str):
#     """Сохраняем новую рекомендацию для преподавателя."""
#     rec = TeacherRecommendation(
#         teacher_id=teacher_id,
#         llm_recommendation=recommendation,
#         updated_at=datetime.now()
#     )
#     session.add(rec)
#     await session.commit()
#     return rec

# # --------------------------------------------------
# # Основная функция (используется в dashboard)
# # --------------------------------------------------

# def get_teacher_recommendation(teacher_id):

#     # 1 проверяем БД
#     recommendation = get_saved_recommendation(teacher_id)

#     if recommendation:
#         return recommendation

#     # 2 считаем метрики
#     metrics = get_teacher_metrics(teacher_id)

#     # 3 генерируем рекомендации
#     rec_list = generate_recommendations(metrics)

#     rec_text = "\n".join(rec_list)

#     # 4 сохраняем
#     save_recommendation(teacher_id, rec_text)

#     return rec_text

import sys
from datetime import datetime
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config import DATABASE_SYNC_URL
from database.models import TeacherRecommendation
from database.session import AsyncSessionLocal

# ----------------- Подключение -----------------
engine = create_engine(DATABASE_SYNC_URL)


# --------------------------------------------------
# Генерация рекомендаций (заглушка вместо LLM)
# --------------------------------------------------
def generate_recommendations(metrics):
    recommendations = []

    avg_rating = metrics.get("avg_rating", 0)
    negative_share = metrics.get("negative_share", 0)

    # --- анализ средней оценки ---
    if avg_rating >= 4.5:
        recommendations.append(
            "Очень высокий уровень удовлетворенности студентов. Рекомендуется сохранить текущие методы преподавания."
        )
    elif 4.0 <= avg_rating < 4.5:
        recommendations.append(
            "Хороший уровень преподавания. Можно дополнительно развивать интерактивные методы обучения."
        )
    elif 3.5 <= avg_rating < 4.0:
        recommendations.append(
            "Средний уровень удовлетворенности. Рекомендуется проанализировать проблемные темы."
        )
    elif 3.0 <= avg_rating < 3.5:
        recommendations.append(
            "Низкая средняя оценка дисциплины. Желательно пересмотреть формат проведения занятий."
        )
    else:
        recommendations.append(
            "Критически низкая средняя оценка. Рекомендуется провести аудит качества преподавания."
        )

    # --- анализ негативных отзывов ---
    if negative_share == 0:
        recommendations.append(
            "Негативных отзывов не обнаружено. Студенты довольны качеством обучения."
        )
    elif 0 < negative_share <= 0.1:
        recommendations.append(
            "Очень низкая доля негативных отзывов."
        )
    elif 0.1 < negative_share <= 0.3:
        recommendations.append(
            "Наблюдается умеренное количество негативных отзывов. Рекомендуется анализ отдельных проблемных тем."
        )
    elif 0.3 < negative_share <= 0.5:
        recommendations.append(
            "Высокая доля негативных отзывов. Необходимо провести корректирующие меры."
        )
    else:
        recommendations.append(
            "Критически высокая доля негативных отзывов. Требуется срочный анализ преподавания."
        )

    return recommendations


# --------------------------------------------------
# Получение метрик преподавателя
# --------------------------------------------------
def get_teacher_metrics(teacher_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT
                    AVG(rating) as avg_rating,
                    AVG(
                        CASE
                            WHEN sentiment = 'negative' THEN 1
                            ELSE 0
                        END
                    ) as negative_share
                FROM feedback
                WHERE teacher = :teacher_id
            """),
            {"teacher_id": teacher_id}
        ).fetchone()

        return {
            "avg_rating": result.avg_rating or 0,
            "negative_share": result.negative_share or 0
        }


# --------------------------------------------------
# Проверка есть ли сохранённая рекомендация
# --------------------------------------------------
def get_saved_recommendation(teacher_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT llm_recommendation
                FROM teacher_recommendations
                WHERE teacher_id = :teacher_id
                ORDER BY updated_at DESC
                LIMIT 1
            """),
            {"teacher_id": teacher_id}
        ).fetchone()

        if result:
            return result[0]

        return None


# --------------------------------------------------
# Асинхронное сохранение рекомендации в БД
# --------------------------------------------------
async def save_teacher_recommendation(session: AsyncSession, teacher_id: int, recommendation: str):
    rec = TeacherRecommendation(
        teacher_id=teacher_id,
        llm_recommendation=recommendation,
        updated_at=datetime.now()
    )
    session.add(rec)
    await session.commit()
    return rec


# --------------------------------------------------
# Основная функция для дашборда
# --------------------------------------------------
def get_teacher_recommendation(teacher_id):
    # 1. Проверяем, есть ли рекомендация в БД
    saved = get_saved_recommendation(teacher_id)
    if saved:
        return saved

    # 2. Считаем метрики
    metrics = get_teacher_metrics(teacher_id)

    # 3. Генерируем рекомендации
    rec_list = generate_recommendations(metrics)
    rec_text = "\n".join(rec_list)

    # 4. Сохраняем асинхронно
    async def save():
        async with AsyncSessionLocal() as session:
            await save_teacher_recommendation(session, teacher_id, rec_text)
    import asyncio
    asyncio.run(save())

    return rec_text
