# from keybert import KeyBERT

# kw_model = KeyBERT()

# def extract_topics(text: str):

#     keywords = kw_model.extract_keywords(
#         text,
#         keyphrase_ngram_range=(1,2),
#         stop_words="russian",
#         top_n=3
#     )

#     topics = [kw[0] for kw in keywords]

#     return topics

from typing import List

from keybert import KeyBERT
from nltk.corpus import stopwords
import nltk

# Скачиваем русские стоп-слова один раз
nltk.download('stopwords')
russian_stopwords = stopwords.words('russian')

# Модель эмбеддингов для KeyBERT
kw_model = KeyBERT(model="sentence-transformers/all-MiniLM-L6-v2")

def extract_topics(text: str) -> List[str]:
    """Выделение топиков из текста"""
    if not text or len(text.split()) < 2:
        return []

    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words=russian_stopwords,
        top_n=3
    )
    topics = [kw[0] for kw in keywords]
    return topics
