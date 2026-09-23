from fastapi import APIRouter, HTTPException
from src.api.v1.schemas.trading import SentimentResponse
from src.nlp.news_fetcher import NewsFetcher
from src.nlp.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()

@router.get("/news/{ticker}", response_model=SentimentResponse)
def get_news_sentiment(ticker: str):
    try:
        fetcher = NewsFetcher()
        news_df = fetcher.fetch_ticker_news(ticker, limit=10)
        
        analyzer = SentimentAnalyzer()
        sentiment_df = analyzer.add_sentiment_features(news_df)

        return SentimentResponse(
            ticker=ticker,
            compound_score=float(sentiment_df["compound_score"].mean()),
            pos_score=float(sentiment_df["pos_score"].mean()),
            neg_score=float(sentiment_df["neg_score"].mean()),
            neu_score=float(sentiment_df["neu_score"].mean())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))