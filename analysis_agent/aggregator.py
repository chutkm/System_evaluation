from collections import Counter

def aggregate_feedback(feedback_list):

    ratings = [f["rating"] for f in feedback_list]

    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    sentiments = Counter(f["sentiment"] for f in feedback_list)

    topics = Counter(
        topic
        for f in feedback_list
        for topic in f["topics"]
    )

    return {
        "avg_rating": avg_rating,
        "sentiment_distribution": dict(sentiments),
        "top_topics": topics.most_common(10)
    }