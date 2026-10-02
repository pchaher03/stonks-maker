import requests
import pandas as pd
import yfinance as yf
from delta.tables import DeltaTable

# In Databricks notebooks and jobs, 'spark' and 'dbutils' are injected globally.
API_KEY = dbutils.secrets.get(scope="stonks_secrets", key="alpha-vantage-api-key")
TARGET_TABLE = "stonks_catalog.bronze.raw_ohlcv"
REQUIRED_COLS = ["date", "ticker", "open", "high", "low", "close", "adj_close", "volume"]

def fetch_yfinance_fallback(symbol: str, period: str) -> pd.DataFrame:
    """Fallback method to fetch OHLCV via yfinance if Alpha Vantage fails."""
    print(f"Falling back to yfinance for {symbol} (period={period})...")
    
    try:
        df = yf.download(tickers=symbol, period=period, interval="1d", progress=False, auto_adjust=True)
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if df.empty:
            raise ValueError(f"yfinance returned empty data for {symbol}.")
            
        df = df.reset_index()
        df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]
        
        if "date" not in df.columns:
            for col in df.columns:
                if "date" in col or "index" in col:
                    df.rename(columns={col: "date"}, inplace=True)
                    break
                    
        df["ticker"] = symbol
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["adj_close"] = df["close"]
        
        return df[REQUIRED_COLS]
    except Exception as e:
        print(f"yfinance fallback failed for {symbol}: {e}")
        return pd.DataFrame(columns=REQUIRED_COLS)

def fetch_alpha_vantage_daily(symbol: str, outputsize: str = "compact") -> pd.DataFrame:
    """Fetches OHLCV data directly from Alpha Vantage with a yfinance fallback."""
    symbol = symbol.upper().strip()
    url = (
        f"https://www.alphavantage.co/query?"
        f"function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"
        f"&outputsize={outputsize}&apikey={API_KEY}"
    )
    
    print(f"Fetching daily OHLCV for {symbol} via Alpha Vantage...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "Time Series (Daily)" in data:
            df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
            df = df.rename(columns={
                "1. open": "open", "2. high": "high", "3. low": "low",
                "4. close": "close", "5. adjusted close": "adj_close", "6. volume": "volume"
            })
            
            df.index = pd.to_datetime(df.index)
            df = df.astype(float).sort_index().reset_index()
            df.rename(columns={"index": "date"}, inplace=True)
            df["ticker"] = symbol
            df["date"] = df["date"].dt.date
            return df[REQUIRED_COLS]
        else:
            reason = data.get("Information") or data.get("Note") or data
            print(f"Alpha Vantage rejected request: {reason}")
            
    except Exception as e:
        print(f"Alpha Vantage request failed: {e}")

    # Fallback execution
    yf_period = "max" if outputsize == "full" else "1y"
    return fetch_yfinance_fallback(symbol, yf_period)

def merge_into_delta(spark_df, table_name: str):
    """Upserts new data into the Delta table."""
    if spark.catalog.tableExists(table_name):
        print(f"Table {table_name} exists. Performing Delta MERGE (Upsert)...")
        delta_table = DeltaTable.forName(spark, table_name)
        
        (delta_table.alias("target")
         .merge(
             source=spark_df.alias("source"),
             condition="target.ticker = source.ticker AND target.date = source.date"
         )
         .whenMatchedUpdateAll()
         .whenNotMatchedInsertAll()
         .execute()
        )
        print("MERGE complete.")
    else:
        print(f"Table {table_name} does not exist. Initializing with OVERWRITE...")
        spark_df.write.format("delta").mode("overwrite").saveAsTable(table_name)
        print("Initialization complete.")

if __name__ == "__main__":
    tickers_to_update = ["AAPL", "NVDA", "TSLA"]
    all_data = []
    
    for ticker in tickers_to_update:
        # Set to "full" to trigger the backfill. AV will block it, and YF will fetch the max history.
        pdf = fetch_alpha_vantage_daily(ticker, outputsize="full")
        if not pdf.empty:
            all_data.append(pdf)
        
    if all_data:
        combined_pdf = pd.concat(all_data, ignore_index=True)
        spark_df = spark.createDataFrame(combined_pdf)
        merge_into_delta(spark_df, TARGET_TABLE)
    else:
        print("Failed to retrieve data for all tickers.")