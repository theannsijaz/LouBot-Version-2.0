"""
Natural Language Processing utilities for LouBot
"""
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Initialize VADER sentiment analyzer
try:
    analyzer = SentimentIntensityAnalyzer()
except LookupError:
    # Download VADER lexicon if not available
    try:
        nltk.download('vader_lexicon', quiet=True)
        analyzer = SentimentIntensityAnalyzer()
    except:
        analyzer = None

def analyze_sentiment(text):
    """
    Analyze sentiment of text using VADER sentiment analyzer
    Returns: dict with compound, pos, neu, neg scores
    """
    if analyzer is None:
        return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}
    
    try:
        scores = analyzer.polarity_scores(text)
        return scores
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}

def get_sentiment_label(compound_score):
    """
    Convert compound score to sentiment label
    """
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"

def process_text_sentiment(text):
    """
    Process text and return sentiment analysis results
    """
    scores = analyze_sentiment(text)
    label = get_sentiment_label(scores['compound'])
    
    return {
        'text': text,
        'sentiment': label,
        'scores': scores,
        'confidence': abs(scores['compound'])
    }

# Additional NLP utilities that might be needed
def clean_text(text):
    """Basic text cleaning"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def extract_keywords(text, max_keywords=5):
    """Simple keyword extraction (can be enhanced with more sophisticated methods)"""
    if not text:
        return []
    
    # Simple approach: split by common words and take most frequent
    words = text.lower().split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    # Filter out stop words and short words
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    
    # Count frequency and return top keywords
    from collections import Counter
    word_freq = Counter(keywords)
    return [word for word, count in word_freq.most_common(max_keywords)] 