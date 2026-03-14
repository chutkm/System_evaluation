from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="blanchefort/rubert-base-cased-sentiment"
)

def analyze_sentiment(text: str) -> str:
    result = classifier(text)[0]

    label = result["label"]

    mapping = {
        "POSITIVE": "positive",
        "NEGATIVE": "negative",
        "NEUTRAL": "neutral"
    }

    return mapping.get(label, "neutral")