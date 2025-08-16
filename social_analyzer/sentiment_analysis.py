from transformers import pipeline
import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

def analyze_sentiment(text):
    try:
        result = sentiment_pipeline(text, truncation=True)[0]
        label = result['label'].lower()
        score = result['score']
        if score < 0.8:
            return 'neutral', 0.0
        return label, score
    except Exception as e:
        print(f"Sentiment analysis failed for text: '{text}'. Error: {e}")
        return 'neutral', 0.0

def analyze_emotion(text):
    try:
        result = emotion_pipeline(text, truncation=True)[0]
        label = result['label'].lower()
        score = result['score']
        return label, score
    except Exception as e:
        print(f"Emotion analysis failed for text: '{text}'. Error: {e}")
        return 'unknown', 0.0

def get_topic_model(texts, num_topics=3, num_words=5):
    if not texts:
        return []
    if len(texts) < 10:
        vectorizer = TfidfVectorizer(stop_words='english')
    else:
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')

    tfidf = vectorizer.fit_transform(texts)

    lda_model = LatentDirichletAllocation(n_components=num_topics, max_iter=5, learning_method='online', random_state=0)
    lda_model.fit(tfidf)

    topic_list = []
    feature_names = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(lda_model.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-num_words - 1:-1]]
        topic_list.append(top_words)
    return topic_list
