import asyncio
from datetime import datetime, timedelta
import logging

# --- Ваши внутренние модули ---
from bot.handlers import get_unprocessed_feedback, update_feedback_analysis
from analysis_agent.sentiment  import analyze_feedback  # NLP-модуль анализа текста
from showcase_agent.llm_recommendations import (
    save_teacher_recommendation,
    get_teacher_metrics,
    generate_recommendations
)
from database.session import AsyncSessionLocal

# --- Настройка периодичности обновлений ---
DAILY_UPDATE_HOUR = 2  # Обновлять рекомендации каждый день в 02:00
CHECK_INTERVAL = 600   # Интервал проверки новых отзывов в секундах (10 минут)

# --- Настройка логирования ---
logging.basicConfig(
    filename="curator_agent.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ------------------------------------------------------------
# 1️⃣ Сбор данных с бота
# ------------------------------------------------------------
async def collect_feedback():
    logging.info("Запуск сбора новых отзывов через бота")
    new_feedback = await get_unprocessed_feedback()
    logging.info(f"Найдено {len(new_feedback)} новых отзывов")
    return new_feedback

# ------------------------------------------------------------
# 2️⃣ Аналитика отзывов
# ------------------------------------------------------------
async def process_feedback(feedback_list):
    logging.info("Запуск аналитики отзывов")
    for fb in feedback_list:
        sentiment, topics = analyze_feedback(fb["text"])
        await update_feedback_analysis(fb["id"], sentiment, topics)
    logging.info("Аналитика завершена")

# ------------------------------------------------------------
# 3️⃣ Генерация и сохранение рекомендаций
# ------------------------------------------------------------
async def update_teacher_recommendations(manual_trigger=False):
    """
    Обновление рекомендаций преподавателей.
    Если manual_trigger=True, обновляем рекомендации независимо от времени.
    """
    logging.info("Обновление рекомендаций преподавателей")

    async with AsyncSessionLocal() as session:
        result = await session.execute("SELECT DISTINCT teacher FROM feedback")
        teacher_ids = [row[0] for row in result.fetchall()]

        for teacher_id in teacher_ids:
            metrics = get_teacher_metrics(teacher_id)
            rec_text = "\n".join(generate_recommendations(metrics))
            await save_teacher_recommendation(session, teacher_id, rec_text)

    logging.info("Рекомендации преподавателей обновлены")

# ------------------------------------------------------------
# 4️⃣ Основной цикл агента-куратора
# ------------------------------------------------------------
async def curator_loop():
    logging.info("Агент-куратор запущен")
    last_daily_update = datetime.now() - timedelta(days=1)

    while True:
        # --- Сбор новых отзывов ---
        new_feedback = await collect_feedback()

        # --- Аналитика только если есть новые отзывы ---
        if new_feedback:
            await process_feedback(new_feedback)

        # --- Ежедневное обновление рекомендаций ---
        now = datetime.now()
        if (now - last_daily_update).days >= 1 and now.hour >= DAILY_UPDATE_HOUR:
            await update_teacher_recommendations()
            last_daily_update = now

        await asyncio.sleep(CHECK_INTERVAL)

# ------------------------------------------------------------
# 5️⃣ Ручной запуск рекомендаций
# ------------------------------------------------------------
async def manual_update_recommendations():
    logging.info("Ручной запуск обновления рекомендаций")
    await update_teacher_recommendations(manual_trigger=True)

# ------------------------------------------------------------
# 6️⃣ Точка входа
# ------------------------------------------------------------
if __name__ == "__main__":
    print("Запуск агента-куратора...")
    logging.info("Старт агента-куратора")
    asyncio.run(curator_loop())
