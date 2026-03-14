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


# async def process_feedback(feedback_id):

#     feedback = await get_feedback_by_id(feedback_id)

#     # sentiment = classify_sentiment(feedback.text)

#     # topics = extract_topics(feedback.text)

#     # await update_feedback_analysis(
#     #     feedback_id,
#     #     sentiment,
#     #     topics
#     # )


from database.repository import get_unprocessed_feedback, update_feedback_analysis

from .sentiment import analyze_sentiment
from .topic_modeling import extract_topics


async def process_feedback(feedback):

    text = feedback["text"]

    sentiment = analyze_sentiment(text)

    topics = extract_topics(text)

    await update_feedback_analysis(
        feedback["id"],
        sentiment,
        topics
    )


async def run_analysis():

    feedback_list = await get_unprocessed_feedback()

    for feedback in feedback_list:

        await process_feedback(feedback)