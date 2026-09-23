import os
import joblib
import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException
from src.api.v1.schemas.trading import ExplanationResponse
from src.models.explainability import ModelExplainer
from src.data.ingestion import MarketDataIngestion
from src.data.spark_pipeline import get_spark_session, SparkTechnicalIndicators
from src.nlp.news_fetcher import NewsFetcher
from src.nlp.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

def compute_pandas_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Computes technical indicators using pure Pandas (RSI, SMA, Bollinger Bands)."""
    df = df.copy()
    
    # Simple Moving Averages
    df["sma_20"] = df["close"].rolling(window=20, min_periods=1).mean()
    df["sma_50"] = df["close"].rolling(window=50, min_periods=1).mean()
    
    # Bollinger Bands
    std_20 = df["close"].rolling(window=20, min_periods=1).std().fillna(0)
    df["bollinger_upper"] = df["sma_20"] + (std_20 * 2)
    df["bollinger_lower"] = df["sma_20"] - (std_20 * 2)
    
    # RSI (14 periods)
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / (loss.replace(0, np.nan))
    df["rsi_14"] = (100 - (100 / (1 + rs))).fillna(50.0)
    
    return df

@router.get("/explain/{ticker}", response_model=ExplanationResponse)
def explain_prediction(ticker: str):
    try:
        reg_model_data = joblib.load(os.path.join(MODELS_DIR, "regressor.joblib"))
        reg_model = reg_model_data["model"]
        features = reg_model_data["features"]

        fetcher = MarketDataIngestion()
        ohlcv = fetcher.fetch_daily_ohlcv(ticker)

        indicators = compute_pandas_indicators(ohlcv)
        
        news_fetcher = NewsFetcher()
        news = news_fetcher.fetch_ticker_news(ticker, limit=10)
        analyzer = SentimentAnalyzer()
        sentiment = analyzer.add_sentiment_features(news)

        latest = indicators.tail(1).copy()
        latest["neg_score"] = sentiment["neg_score"].mean() if not sentiment.empty else 0.0
        latest["neu_score"] = sentiment["neu_score"].mean() if not sentiment.empty else 1.0
        latest["pos_score"] = sentiment["pos_score"].mean() if not sentiment.empty else 0.0
        latest["compound_score"] = sentiment["compound_score"].mean() if not sentiment.empty else 0.0

        X = latest[features]

        explainer = ModelExplainer(reg_model, features)
        explanation = explainer.explain_instance(X)

        return ExplanationResponse(
            ticker=ticker,
            base_value=explanation["base_value"],
            feature_contributions=explanation["feature_contributions"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))