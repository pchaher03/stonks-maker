import os
import joblib
import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException
from src.api.v1.schemas.trading import PredictionRequest, PredictionResponse
from src.data.ingestion import MarketDataIngestion
from src.data.spark_pipeline import get_spark_session, SparkTechnicalIndicators
from src.nlp.news_fetcher import NewsFetcher
from src.nlp.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()

# Resolve models directory relative to project root /app
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

@router.post("/predictions", response_model=PredictionResponse)
def get_prediction(payload: PredictionRequest):
    try:
        reg_path = os.path.join(MODELS_DIR, "regressor.joblib")
        dir_path = os.path.join(MODELS_DIR, "direction_clf.joblib")
        strat_path = os.path.join(MODELS_DIR, "strategy_clf.joblib")

        if not os.path.exists(reg_path):
            raise FileNotFoundError(f"Model file missing at: {reg_path}")

        reg_model_data = joblib.load(reg_path)
        dir_model_data = joblib.load(dir_path)
        strat_model_data = joblib.load(strat_path)
        
        reg_model = reg_model_data["model"]
        dir_model = dir_model_data["model"]
        strat_model = strat_model_data["model"]
        features = reg_model_data["features"]

        fetcher = MarketDataIngestion()
        ohlcv = fetcher.fetch_daily_ohlcv(payload.ticker)

        indicators = compute_pandas_indicators(ohlcv)
        
        news_fetcher = NewsFetcher()
        news = news_fetcher.fetch_ticker_news(payload.ticker, limit=10)
        analyzer = SentimentAnalyzer()
        sentiment = analyzer.add_sentiment_features(news)

        latest = indicators.tail(1).copy()
        latest["neg_score"] = sentiment["neg_score"].mean() if not sentiment.empty else 0.0
        latest["neu_score"] = sentiment["neu_score"].mean() if not sentiment.empty else 1.0
        latest["pos_score"] = sentiment["pos_score"].mean() if not sentiment.empty else 0.0
        latest["compound_score"] = sentiment["compound_score"].mean() if not sentiment.empty else 0.0

        X = latest[features]

        target_price = float(reg_model.predict(X)[0])
        direction_pred = dir_model.predict(X)[0]
        strategy_pred = strat_model.predict(X)[0]

        return PredictionResponse(
            ticker=payload.ticker,
            target_price=target_price,
            direction="UP" if direction_pred == 1 else "DOWN",
            recommended_strategy=str(strategy_pred)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))