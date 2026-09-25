import pandas as pd
import numpy as np
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from src.api.v1.schemas.trading import ExplanationResponse
from src.api.dependencies import (
    get_models,
    get_market_ingestion,
    get_news_fetcher,
    get_sentiment_analyzer
)
from src.models.explainability import ModelExplainer
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

@router.get("/explain/{ticker}", response_model=ExplanationResponse)
def explain_prediction(
    ticker: str,
    models: Dict[str, Any] = Depends(get_models),
    ingestion: MarketDataIngestion = Depends(get_market_ingestion),
    news_fetcher: NewsFetcher = Depends(get_news_fetcher),
    analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer)
):
    try:
        reg_model = models["reg_model"]
        features = models["features"]

        ohlcv = ingestion.fetch_daily_ohlcv(ticker)
        indicators = compute_pandas_indicators(ohlcv)

        news = news_fetcher.fetch_ticker_news(ticker, limit=10)
        sentiment = analyzer.add_sentiment_features(news, text_column="text")

        latest = indicators.tail(1).copy()
        latest["neg_score"] = sentiment["neg_score"].mean() if not sentiment.empty and "neg_score" in sentiment.columns else 0.0
        latest["neu_score"] = sentiment["neu_score"].mean() if not sentiment.empty and "neu_score" in sentiment.columns else 1.0
        latest["pos_score"] = sentiment["pos_score"].mean() if not sentiment.empty and "pos_score" in sentiment.columns else 0.0
        latest["compound_score"] = sentiment["compound_score"].mean() if not sentiment.empty and "compound_score" in sentiment.columns else 0.0

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