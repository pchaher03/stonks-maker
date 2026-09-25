from fastapi import APIRouter, Depends, HTTPException
from src.api.v1.schemas.trading import SentimentResponse
from src.api.dependencies import get_news_fetcher, get_sentiment_analyzer
from src.nlp.news_fetcher import NewsFetcher
from src.nlp.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()

@router.get("/news/{ticker}", response_model=SentimentResponse)
def get_news_sentiment(
    ticker: str,
    news_fetcher: NewsFetcher = Depends(get_news_fetcher),
    analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer)
):
    try:
        news_df = news_fetcher.fetch_ticker_news(ticker, limit=10)
        sentiment_df = analyzer.add_sentiment_features(news_df, text_column="text")

        return SentimentResponse(
            ticker=ticker,
            compound_score=float(sentiment_df["compound_score"].mean()) if not sentiment_df.empty and "compound_score" in sentiment_df.columns else 0.0,
            pos_score=float(sentiment_df["pos_score"].mean()) if not sentiment_df.empty and "pos_score" in sentiment_df.columns else 0.0,
            neg_score=float(sentiment_df["neg_score"].mean()) if not sentiment_df.empty and "neg_score" in sentiment_df.columns else 0.0,
            neu_score=float(sentiment_df["neu_score"].mean()) if not sentiment_df.empty and "neu_score" in sentiment_df.columns else 1.0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))