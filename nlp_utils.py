# nlp_utils.py

from textblob import TextBlob
from transformers import pipeline
import re

# Loading the summarization pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Sentiment Analyzer
def get_sentiment(text: str) -> str:
    """
    Analyzes sentiment using TextBlob.
    Returns one of: 'Positive', 'Negative', 'Neutral'
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.2:
        return "Positive"
    elif polarity < -0.2:
        return "Negative"
    else:
        return "Neutral"


# Summarizer
def summarize_review(text: str) -> str:
    """
    Summarizes the review content if it's long enough.
    Short reviews are returned as-is.
    """
    text = re.sub(r"\s+", " ", text.strip())

    if len(text.split()) < 30:
        return text 

    try:
        summary = summarizer(
            text, max_length=60, min_length=20, do_sample=False
        )[0]['summary_text']
        return summary.strip()
    except Exception:
        return text


# Tip Generator
def generate_improvement_tip(sentiment: str, text: str) -> str:
    """
    Generates suggestions for improvement based on sentiment and keywords in the review.
    """
    text_lower = text.lower()

    if sentiment == "Negative":
        if "battery" in text_lower:
            return "Users are disappointed with the battery life."
        elif "delivery" in text_lower or "packaging" in text_lower:
            return "Delivery experience or packaging needs attention."
        elif "sound" in text_lower or "audio" in text_lower:
            return "Sound quality might require enhancement."
        elif "price" in text_lower:
            return "Customers feel the product isn't worth the price."
        elif "quality" in text_lower or "build" in text_lower:
            return "Consider improving build or quality control."
        else:
            return "Check user complaints for common recurring issues."

    elif sentiment == "Neutral":
        return "Explore subtle improvements in experience or support."

    else:  # Positive
        return "Keep up the good work — users are satisfied!"
