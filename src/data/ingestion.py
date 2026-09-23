import requests
import pandas as pd
import yfinance as yf
from typing import Optional
from src.core.config import settings
from src.core.logger import logger

REQUIRED_COLS = ["date", "ticker", "open", "high", "low", "close", "adj_close", "volume"]

class MarketDataIngestion:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ALPHA_VANTAGE_API_KEY

    def fetch_daily_ohlcv(self, symbol: str, outputsize: str = "compact") -> pd.DataFrame:
        """
        Fetches Daily OHLCV data from Alpha Vantage or falls back to yfinance.
        """
        symbol = symbol.upper().strip()

        # 1. Try Alpha Vantage if a valid key is set
        if self.api_key and "your_" not in self.api_key and len(self.api_key.strip()) > 0:
            url = (
                f"https://www.alphavantage.co/query?"
                f"function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"
                f"&outputsize={outputsize}&apikey={self.api_key}"
            )
            logger.info(f"Fetching daily OHLCV for {symbol} via Alpha Vantage...")
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200 and response.text.strip():
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
                        # Keep only the agreed-upon schema (drops dividend amount,
                        # split coefficient, etc. so both sources match).
                        return df[REQUIRED_COLS]
                    else:
                        # AV returns 200 with a JSON body like {"Note": ...} or
                        # {"Information": ...} when rate-limited or the symbol is bad.
                        reason = data.get("Note") or data.get("Information") or data.get("Error Message") or data
                        logger.warning(
                            f"Alpha Vantage returned no time series for {symbol}: {reason}. "
                            f"Falling back to yfinance."
                        )
                else:
                    logger.warning(
                        f"Alpha Vantage request for {symbol} returned status "
                        f"{response.status_code}. Falling back to yfinance."
                    )
            except Exception as e:
                logger.warning(f"Alpha Vantage fetch failed ({e}). Falling back to yfinance.")

        # 2. Fallback to yfinance with browser header session
        return self._fetch_yfinance(symbol)

    def _fetch_yfinance(self, symbol: str) -> pd.DataFrame:
        logger.info(f"Fetching OHLCV for {symbol} via yfinance...")

        # NOTE: yfinance's default session can be blocked by Yahoo anti-scraping measures.
        session = None
        try:
            from curl_cffi import requests as curl_requests
            session = curl_requests.Session(impersonate="chrome")
        except ImportError:
            logger.warning(
                "curl_cffi not installed; falling back to yfinance's default session. "
                "session. Install curl_cffi for better reliability against Yahoo anti-scraping blocks."
                "pip install curl_cffi"
            )

        df = pd.DataFrame()

        # Download with session
        download_kwargs = dict(
            tickers=symbol,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )
        if session is not None:
            download_kwargs["session"] = session

        try:
            df = yf.download(**download_kwargs)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
        except Exception as e:
            logger.warning(f"yf.download failed for {symbol}: {e}")

        # Ticker history fallback
        if df.empty:
            try:
                ticker_kwargs = {"session": session} if session is not None else {}
                ticker = yt.Ticker(symbol, **ticker_kwargs)
                df = ticker.history(period="1y", auto_adjust=True)
            except Exception as e:
                logger.warning(f"yf.Ticker.history failed for {symbol}: {e}")

        if df.empty:
            raise ValueError(f"Unable to retrieve market data for '{symbol}'. Check symbol or network connection")

        df = df.reset_index()
        df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

        # Normalize date column name
        if "date" not in df.columns:
            for col in df.columns:
                if "date" in col or "index" in col:
                    df.rename(columns={col: "date"}, inplace=True)
                    break

        df["ticker"] = symbol
        df["date"] = pd.to_datetime(df["date"]).dt.date

        # auto_adjust=True means 'close' is already adjusted; mirror it into
        # 'adj_close' so this path matches the Alpha Vantage schema exactly.
        df["adj_close"] = df["close"]

        return df[REQUIRED_COLS]