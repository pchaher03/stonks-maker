import requests
import pandas as pd
import yfinance as yf
from typing import Optional
from src.core.config import settings
from src.core.logger import logger

COLS = ["timestamp", "ticker", "title", "text", "source", "url"]

# Tickers that Yahoo may tag interchangeably in relatedTickers
TICKER_ALIASES = {
    "GOOGL": {"GOOGL", "GOOG"},
    "GOOG": {"GOOG", "GOOGL"},
}


class NewsFetcher:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.NEWS_API_KEY

    @staticmethod
    def _dig(d, *keys, default=None):
        """Safely traverse nested dictionaries without raising AttributeError on None values."""
        for k in keys:
            if not isinstance(d, dict):
                return default
            d = d.get(k)
        return d if d is not None else default

    def fetch_ticker_news(self, ticker: str, limit: int = 20) -> pd.DataFrame:
        """
        Fetches news articles for a given ticker symbol.
        Tries NewsAPI first (if a key is configured); falls back to Yahoo Finance search news.
        """
        ticker = ticker.upper().strip()

        # 1. Try NewsAPI if a valid key is configured
        if self.api_key and "your_" not in self.api_key and len(self.api_key.strip()) > 0:
            try:
                logger.info(f"Fetching news for {ticker} via NewsAPI...")
                query = f"{ticker} stock" if len(ticker) <= 2 else ticker
                url = (
                    f"https://newsapi.org/v2/everything?"
                    f"q={query}&sortBy=publishedAt&pageSize={limit}&apiKey={self.api_key}"
                )
                res = requests.get(url, timeout=10)
                if res.status_code == 200 and res.text.strip():
                    data = res.json()
                    if data.get("status") == "ok" and data.get("articles"):
                        articles = []
                        for item in data["articles"]:
                            title = str(item.get("title") or "").strip()
                            description = str(item.get("description") or "").strip()

                            if not title or title.lower() in ["none", "null"]:
                                continue

                            articles.append({
                                "timestamp": pd.to_datetime(item.get("publishedAt"), utc=True, errors="coerce"),
                                "ticker": ticker,
                                "title": title,
                                "text": f"{title}. {description}".strip(),
                                "source": item.get("source", {}).get("name", "NewsAPI"),
                                "url": item.get("url", "#")
                            })

                        if articles:
                            df = pd.DataFrame(articles)
                            return df[COLS]
                else:
                    logger.warning(f"NewsAPI returned status {res.status_code}. Falling back to yfinance.")
            except Exception as e:
                logger.warning(f"NewsAPI request failed ({e}). Falling back to yfinance.")

        # 2. Fall back to Yahoo Finance
        return self._fetch_yfinance_news(ticker, limit)

    def _fetch_yfinance_news_items(self, ticker: str, limit: int) -> list:
        """
        Gets raw news items from Yahoo using yf.Search.
        """
        items = []

        # Primary: Search news
        try:
            search_count = max(limit * 2, 10)
            raw = yf.Search(ticker, news_count=search_count).news or []
            accepted = TICKER_ALIASES.get(ticker, {ticker})
            for n in raw:
                related = {str(t).upper() for t in (n.get("relatedTickers") or [])}
                # Keep items with no relatedTickers, or that mention this ticker
                if not related or related & accepted:
                    items.append(n)
            logger.info(f"{ticker}: yf.Search returned {len(raw)} items, {len(items)} relevant.")
        except Exception as e:
            logger.warning(f"yf.Search news failed for {ticker}: {e}")

        # Secondary: legacy Ticker.news
        if not items:
            try:
                items = yf.Ticker(ticker).news or []
                if items:
                    logger.info(f"{ticker}: legacy Ticker.news returned {len(items)} items.")
            except Exception as e:
                logger.warning(f"Legacy Ticker.news failed for {ticker}: {e}")

        return items

    def _fetch_yfinance_news(self, ticker: str, limit: int) -> pd.DataFrame:
        logger.info(f"Fetching news for {ticker} via yfinance fallback...")

        news_data = self._fetch_yfinance_news_items(ticker, limit)
        if not news_data:
            logger.warning(f"No news items returned by Yahoo for {ticker}.")
            return pd.DataFrame(columns=COLS)

        articles = []
        seen_titles = set()

        for item in news_data:
            if len(articles) >= limit:
                break

            try:
                # Handles both the nested "content" schema and the flat search schema
                content = item.get("content") if isinstance(item.get("content"), dict) else item

                # Exclude video/audio media items
                content_type = str(content.get("contentType") or item.get("type") or "").upper()
                if any(media in content_type for media in ["VIDEO", "AUDIO", "PODCAST"]):
                    continue

                title = str(content.get("title") or item.get("title") or "").strip()
                summary = str(content.get("summary") or item.get("summary") or "").strip()

                if not title or title.lower() in ["none", "null"]:
                    continue

                # Deduplicate by headline
                key = title.lower()
                if key in seen_titles:
                    continue
                seen_titles.add(key)

                # Timestamp: epoch seconds (search) or ISO string (nested)
                pub_time = content.get("pubDate") or item.get("providerPublishTime")
                if isinstance(pub_time, (int, float)):
                    ts = pd.to_datetime(pub_time, unit="s", utc=True)
                else:
                    ts = pd.to_datetime(pub_time, utc=True, errors="coerce")

                article_url = (
                    self._dig(content, "canonicalUrl", "url")
                    or self._dig(content, "clickThroughUrl", "url")
                    or item.get("link")
                    or "#"
                )

                publisher = (
                    self._dig(content, "provider", "displayName")
                    or item.get("publisher")
                    or "yfinance"
                )

                articles.append({
                    "timestamp": ts,
                    "ticker": ticker,
                    "title": title,
                    "text": f"{title}. {summary}".strip() if summary else title,
                    "source": publisher,
                    "url": article_url
                })
            except Exception as inner_e:
                logger.warning(f"Skipped malformed news item for {ticker}: {inner_e}")
                continue

        if articles:
            return pd.DataFrame(articles)[COLS]

        logger.warning(f"No valid news articles found for {ticker}. Returning empty DataFrame fallback.")
        return pd.DataFrame(columns=COLS)