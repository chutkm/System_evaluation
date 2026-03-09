# # from analysis_agent.sentiment import classify_sentiment
# # from analysis_agent.topic_modeling import extract_topics
# from database.repository import (
#     get_feedback_by_id,
#     update_feedback_analysis,
# )
# # from analysis_agent.aggregator import calculate_statistics


# async def process_feedback(feedback_id: int):
#     feedback = await get_feedback_by_id(feedback_id)

#     if not feedback:
#         return

#     # sentiment = classify_sentiment(feedback.text)
#     # topics = extract_topics(feedback.text)

#     # await update_feedback_analysis(feedback, sentiment, topics)
#     # await calculate_statistics()

# from analysis_agent.sentiment import classify_sentiment
# from analysis_agent.topic_modeling import extract_topics

from database.repository import get_feedback_by_id
# from database.repository import update_feedback_analysis


async def process_feedback(feedback_id):

    feedback = await get_feedback_by_id(feedback_id)

    # sentiment = classify_sentiment(feedback.text)

    # topics = extract_topics(feedback.text)

    # await update_feedback_analysis(
    #     feedback_id,
    #     sentiment,
    #     topics
    # )