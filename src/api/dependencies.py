import os
import joblib
from typing import Dict, Any, List
from fastapi import HTTPException
from src.core.config import get_feature_list, get_default_tickers
from src.data.ingestion import MarketDataIngestion
from src.nlp.news_fetcher import NewsFetcher
from src.nlp.sentiment_analyzer import SentimentAnalyzer

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

_ingestion_client = None
_news_fetcher = None
_sentiment_analyzer = None

def get_models() -> Dict[str, Any]:
    """Loads pre-trained ML models and supplies configured feature names."""
    reg_path = os.path.join(MODELS_DIR, "regressor.joblib")
    dir_path = os.path.join(MODELS_DIR, "direction_clf.joblib")
    strat_path = os.path.join(MODELS_DIR, "strategy_clf.joblib")

    if not os.path.exists(reg_path):
        raise HTTPException(
            status_code=500, 
            detail=f"Model files missing at: {MODELS_DIR}. Ensure Phase 5 cross-validation has run."
        )

    try:
        reg_model_data = joblib.load(reg_path)
        dir_model_data = joblib.load(dir_path)
        strat_model_data = joblib.load(strat_path)

        # Fallback to YAML features if binary attributes are missing
        features = reg_model_data.get("features") or get_feature_list()

        return {
            "reg_model": reg_model_data["model"],
            "dir_model": dir_model_data["model"],
            "strat_model": strat_model_data["model"],
            "features": features
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model binaries: {e}")

def get_market_ingestion() -> MarketDataIngestion:
    global _ingestion_client
    if _ingestion_client is None:
        _ingestion_client = MarketDataIngestion()
    return _ingestion_client

def get_news_fetcher() -> NewsFetcher:
    global _news_fetcher
    if _news_fetcher is None:
        _news_fetcher = NewsFetcher()
    return _news_fetcher

def get_sentiment_analyzer() -> SentimentAnalyzer:
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer

def get_configured_tickers() -> List[str]:
    """Dependency provider returning default tickers configured in config/config.yaml."""
    return get_default_tickers()