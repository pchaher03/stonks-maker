import pandas as pd
import numpy as np
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from src.api.v1.schemas.trading import PredictionRequest, PredictionResponse
from src.api.dependencies import (
    get_models,
    get_market_ingestion,
    get_news_fetcher,
    get_sentiment_analyzer
)
from src.data.ingestion import MarketDataIngestion
from src.nlp.news_fetcher import NewsFetcher
from src.nlp.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()

def compute_pandas_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Computes technical indicators using pure Pandas."""
    df = df.copy()
    df["sma_20"] = df["close"].rolling(window=20, min_periods=1).mean()
    df["sma_50"] = df["close"].rolling(window=50, min_periods=1).mean()
    
    std_20 = df["close"].rolling(window=20, min_periods=1).std().fillna(0)
    df["bollinger_upper"] = df["sma_20"] + (std_20 * 2)
    df["bollinger_lower"] = df["sma_20"] - (std_20 * 2)
    
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / (loss.replace(0, np.nan))
    df["rsi_14"] = (100 - (100 / (1 + rs))).fillna(50.0)
    return df

@router.post("/predictions", response_model=PredictionResponse)
def get_prediction(
    payload: PredictionRequest,
    models: Dict[str, Any] = Depends(get_models),
    ingestion: MarketDataIngestion = Depends(get_market_ingestion),
    news_fetcher: NewsFetcher = Depends(get_news_fetcher),
    analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer)
):
    try:
        reg_model = models["reg_model"]
        dir_model = models["dir_model"]
        strat_model = models["strat_model"]
        features = models["features"]

        # 1. Fetch market data & compute technical indicators
        ohlcv = ingestion.fetch_daily_ohlcv(payload.ticker)
        indicators = compute_pandas_indicators(ohlcv)

        # 2. Fetch news & compute sentiment features
        news = news_fetcher.fetch_ticker_news(payload.ticker, limit=10)
        sentiment = analyzer.add_sentiment_features(news, text_column="text")

        # 3. Assemble single-row feature vector
        latest = indicators.tail(1).copy()
        latest["neg_score"] = sentiment["neg_score"].mean() if not sentiment.empty and "neg_score" in sentiment.columns else 0.0
        latest["neu_score"] = sentiment["neu_score"].mean() if not sentiment.empty and "neu_score" in sentiment.columns else 1.0
        latest["pos_score"] = sentiment["pos_score"].mean() if not sentiment.empty and "pos_score" in sentiment.columns else 0.0
        latest["compound_score"] = sentiment["compound_score"].mean() if not sentiment.empty and "compound_score" in sentiment.columns else 0.0

        X = latest[features]

        # 4. Perform live model inferences
        predicted_return = float(reg_model.predict(X)[0])
        current_price = float(latest["close"].iloc[-1])
        target_price = current_price * (1 + predicted_return)

        direction_pred = dir_model.predict(X)[0]
        strategy_pred = strat_model.predict(X)[0]

        return PredictionResponse(
            ticker=payload.ticker,
            target_price=round(target_price, 2),
            direction="UP" if direction_pred == 1 else "DOWN",
            recommended_strategy=str(strategy_pred)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))