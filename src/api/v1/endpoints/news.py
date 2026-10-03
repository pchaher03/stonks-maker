import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from src.api.v1.schemas.trading import SentimentResponse, ArticleItem
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
        
        if news_df.empty:
            return SentimentResponse(
                ticker=ticker,
                compound_score=0.0,
                pos_score=0.0,
                neg_score=0.0,
                neu_score=1.0,
                articles=[]
            )

        sentiment_df = analyzer.add_sentiment_features(news_df, text_column="text")

        articles_list = []
        for _, row in sentiment_df.iterrows():
            title_val = str(row.get("title") or "").strip()
            if not title_val or title_val.lower() in ["none", "null"]:
                continue

            ts = row.get("timestamp")
            ts_str = str(ts) if pd.notna(ts) and ts is not None else None
            source_val = str(row.get("source") or "Financial News")
            url_val = str(row.get("url")) if "url" in row and pd.notna(row.get("url")) else "#"
            score_val = float(row.get("compound_score", 0.0)) if pd.notna(row.get("compound_score")) else 0.0

            articles_list.append(
                ArticleItem(
                    title=title_val,
                    source=source_val,
                    timestamp=ts_str,
                    url=url_val,
                    compound_score=score_val
                )
            )

        comp_mean = float(sentiment_df["compound_score"].mean()) if "compound_score" in sentiment_df.columns and not sentiment_df["compound_score"].isna().all() else 0.0
        pos_mean = float(sentiment_df["pos_score"].mean()) if "pos_score" in sentiment_df.columns and not sentiment_df["pos_score"].isna().all() else 0.0
        neg_mean = float(sentiment_df["neg_score"].mean()) if "neg_score" in sentiment_df.columns and not sentiment_df["neg_score"].isna().all() else 0.0
        neu_mean = float(sentiment_df["neu_score"].mean()) if "neu_score" in sentiment_df.columns and not sentiment_df["neu_score"].isna().all() else 1.0

        return SentimentResponse(
            ticker=ticker,
            compound_score=comp_mean,
            pos_score=pos_mean,
            neg_score=neg_mean,
            neu_score=neu_mean,
            articles=articles_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))