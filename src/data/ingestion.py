import requests
import pandas as pd
from typing import Optional
from src.core.config import settings
from src.core.logger import logger

class MarketDataIngestion:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ALPHA_VANTAGE_API_KEY

    def fetch_daily_ohlcv(self, symbol: str, outputsize: str = "compact") -> pd.DataFrame:
        """
        Fetches Daily OHLCV data from Alpha Vantage.
        Fallback to yfinance if key is placeholder or request fails.
        """
        symbol = symbol.upper()
        if self.api_key and "your_" not in self.api_key:
            url = (
                f"https://www.alphavantage.co/query?"
                f"function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"
                f"&outputsize={outputsize}&apikey={self.api_key}"
            )
            logger.info(f"Fetching daily OHLCV for {symbol} via Alpha Vantage...")
            response = requests.get(url)
            data = response.json()

            if "Time Series (Daily)" in data:
                df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
                df = df.rename(columns={
                    "1. open": "open",
                    "2. high": "high",
                    "3. low": "low",
                    "4. close": "close",
                    "5. adjusted close": "adj_close",
                    "6. volume": "volume"
                })
                df.index = pd.to_datetime(df.index)
                df = df.astype(float).sort_index().reset_index()
                df.rename(columns={"index": "date"}, inplace=True)
                df["ticker"] = symbol
                return df
            else:
                logger.warning(f"Alpha Vantage response invalid or rate limited. Falling back to yfinance.")

        # Fallback to yfinance
        return self._fetch_yfinance(symbol)

    def _fetch_yfinance(self, symbol: str) -> pd.DataFrame:
        import yfinance as yf
        logger.info(f"Fetching OHLCV for {symbol} via yfinance...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        df = df.reset_index()
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
        df["ticker"] = symbol
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']]