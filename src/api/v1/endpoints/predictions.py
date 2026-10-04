import pandas as pd
import numpy as np
import yfinance as yf
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

def parse_horizon_days(horizon_input: Any) -> int:
    """Converts horizon inputs (int or string like '1D', '5D', '1M') to trading days."""
    if isinstance(horizon_input, int):
        return max(1, horizon_input)
    
    mapping = {
        "1D": 1,
        "5D": 5,
        "1M": 21,
    }
    return mapping.get(str(horizon_input).upper(), 1)

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

        horizon_days = payload.horizon or 1

        # 1. Fetch market data & compute technical indicators
        symbol = payload.ticker.upper().strip()
        ohlcv = ingestion.fetch_daily_ohlcv(symbol)
        indicators = compute_pandas_indicators(ohlcv)

        # Fetch the latest company name if available
        company_name = symbol
        try:
            ticker_info = yf.Ticker(symbol).info
            company_name = ticker_info.get("shortName") or ticker_info.get("longName") or symbol
        except Exception:
            company_name = symbol  # Fallback to symbol if network metadata lookup fails

        # 2. Fetch news & compute sentiment features
        news = news_fetcher.fetch_ticker_news(symbol, limit=10)
        sentiment = analyzer.add_sentiment_features(news, text_column="text")

        # 3. Assemble single-row feature vector
        latest = indicators.tail(1).copy()
        latest["neg_score"] = sentiment["neg_score"].mean() if not sentiment.empty and "neg_score" in sentiment.columns else 0.0
        latest["neu_score"] = sentiment["neu_score"].mean() if not sentiment.empty and "neu_score" in sentiment.columns else 1.0
        latest["pos_score"] = sentiment["pos_score"].mean() if not sentiment.empty and "pos_score" in sentiment.columns else 0.0
        latest["compound_score"] = sentiment["compound_score"].mean() if not sentiment.empty and "compound_score" in sentiment.columns else 0.0

        X = latest[features]

        # 4. Perform inferences
        daily_predicted_return = float(reg_model.predict(X)[0])
        current_price = float(latest["close"].iloc[-1])

        # Scale expected return compound rate across horizon days
        horizon_predicted_return = ((1 + daily_predicted_return) ** horizon_days) - 1
        target_price = current_price * (1 + horizon_predicted_return)

        if horizon_days == 1:
            direction_pred = dir_model.predict(X)[0]
            direction = "UP" if direction_pred == 1 else "DOWN"
            recommended_strategy = str(strat_model.predict(X)[0])
        else:
            direction = "UP" if horizon_predicted_return >= 0 else "DOWN"
            recommended_strategy = "Swing Trading"

        return PredictionResponse(
            ticker=symbol,
            company_name=company_name,
            current_price=round(current_price, 2),
            target_price=round(target_price, 2),
            direction=direction,
            recommended_strategy=recommended_strategy
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))