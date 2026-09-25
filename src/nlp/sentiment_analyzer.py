import pandas as pd
import nltk
from typing import Dict, List, Optional
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from src.core.config import get_model_params
from src.core.logger import logger

# Ensure VADER lexicon is available silently
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        params = get_model_params().get("features", {})
        self.configured_sentiment_cols = params.get(
            "sentiment", 
            ["neg_score", "neu_score", "pos_score", "compound_score"]
        )

    def analyze_text(self, text: str) -> Dict[str, float]:
        """Calculates VADER sentiment polarity scores for a text string."""
        if not text or not isinstance(text, str):
            return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}
        return self.vader.polarity_scores(text)

    def add_sentiment_features(self, df: pd.DataFrame, text_column: str = "title") -> pd.DataFrame:
        """
        Applies sentiment analysis across a DataFrame column containing news text.
        Outputs normalized sentiment columns matching config/model_params.yaml.
        """
        if df.empty or text_column not in df.columns:
            logger.warning(f"DataFrame is empty or missing '{text_column}' column for sentiment analysis.")
            return df

        logger.info("Computing sentiment scores for news dataset...")
        scores = df[text_column].apply(self.analyze_text)
        scores_df = pd.DataFrame(scores.tolist())

        # Map to configured feature names
        df["neg_score"] = scores_df["neg"]
        df["neu_score"] = scores_df["neu"]
        df["pos_score"] = scores_df["pos"]
        df["compound_score"] = scores_df["compound"]

        logger.info("Sentiment scoring completed successfully.")
        return df