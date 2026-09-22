import requests
import pandas as pd
import yfinance as yf
from typing import List, Dict, Optional
from src.core.config import settings
from src.core.logger import logger

class NewsFetcher:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.NEWS_API_KEY

    def fetch_ticker_news(self, ticker: str, limit: int = 20) -> pd.DataFrame:
        """
        Fetches news articles for a given ticker symbol.
        Tries NewsAPI first; falls back to yfinance news feed.
        """
        ticker = ticker.upper()
        if self.api_key and "your_" not in self.api_key:
            try:
                logger.info(f"Fetching news for {ticker} via NewsAPI...")
                url = (
                    f"https://newsapi.org/v2/everything?"
                    f"q={ticker}&sortBy=publishedAt&pageSize={limit}&apiKey={self.api_key}"
                )
                res = requests.get(url, timeout=10)
                data = res.json()
                if data.get("status") == "ok" and data.get("articles"):
                    articles = []
                    for item in data["articles"]:
                        articles.append({
                            "timestamp": pd.to_datetime(item.get("publishedAt")),
                            "ticker": ticker,
                            "title": item.get("title", ""),
                            "description": item.get("description", "") or "",
                            "source": item.get("source", {}).get("name", "NewsAPI")
                        })
                    df = pd.DataFrame(articles)
                    df["text"] = df["title"] + ". " + df["description"]
                    return df[["timestamp", "ticker", "title", "text", "source"]]
            except Exception as e:
                logger.warning(f"NewsAPI request failed ({e}). Falling back to yfinance.")

        return self._fetch_yfinance_news(ticker, limit)

    def _fetch_yfinance_news(self, ticker: str, limit: int) -> pd.DataFrame:
        logger.info(f"Fetching news for {ticker} via yfinance fallback...")
        yf_ticker = yf.Ticker(ticker)
        news_data = yf_ticker.news or []
        articles = []
        for item in news_data[:limit]:
            # Handle variations in yfinance news dictionary schema
            content = item.get("content", {}) if isinstance(item.get("content"), dict) else item
            title = content.get("title") or item.get("title", "")
            summary = content.get("summary") or item.get("summary", "")
            pub_time = content.get("pubDate") or item.get("providerPublishTime")
            
            articles.append({
                "timestamp": pd.to_datetime(pub_time, unit="s" if isinstance(pub_time, (int, float)) else None),
                "ticker": ticker,
                "title": title,
                "text": f"{title}. {summary}".strip(),
                "source": item.get("publisher") or content.get("provider", {}).get("displayName", "yfinance")
            })

        df = pd.DataFrame(articles)
        if df.empty:
            logger.warning(f"No news articles found for {ticker}.")
            return pd.DataFrame(columns=["timestamp", "ticker", "title", "text", "source"])
            
        return df[["timestamp", "ticker", "title", "text", "source"]]