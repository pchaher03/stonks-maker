import requests
import pandas as pd
from delta.tables import DeltaTable

# In Databricks notebooks and jobs, 'spark' and 'dbutils' are injected globally.
# We fetch the secret directly from the Key Vault-backed scope we provisioned in Terraform.
API_KEY = dbutils.secrets.get(scope="stonks_secrets", key="alpha-vantage-api-key")
TARGET_TABLE = "stonks_catalog.bronze.raw_ohlcv"
REQUIRED_COLS = ["date", "ticker", "open", "high", "low", "close", "adj_close", "volume"]

def fetch_alpha_vantage_daily(symbol: str, outputsize: str = "compact") -> pd.DataFrame:
    """Fetches OHLCV data directly from Alpha Vantage."""
    symbol = symbol.upper().strip()
    url = (
        f"https://www.alphavantage.co/query?"
        f"function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"
        f"&outputsize={outputsize}&apikey={API_KEY}"
    )
    
    print(f"Fetching daily OHLCV for {symbol}...")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if "Time Series (Daily)" not in data:
        raise ValueError(f"API Error or Rate Limit for {symbol}: {data}")
        
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
    df["date"] = df["date"].dt.date
    
    return df[REQUIRED_COLS]

def merge_into_delta(spark_df, table_name: str):
    """
    Upserts new data into the Delta table. 
    Creates the table if it does not exist (initial backfill).
    """
    # Check if the table exists in the Unity Catalog metastore
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

# --- Execution Entrypoint ---
if __name__ == "__main__":
    # Example list of tickers to update daily
    tickers_to_update = ["AAPL", "NVDA", "TSLA"]
    
    all_data = []
    for ticker in tickers_to_update:
        # For historical backfill, change outputsize to "full"
        # For daily runs, keep as "compact" (last 100 days)
        pdf = fetch_alpha_vantage_daily(ticker, outputsize="full")
        all_data.append(pdf)
        
    # Combine all fetched pandas DataFrames and convert to a PySpark DataFrame
    combined_pdf = pd.concat(all_data, ignore_index=True)
    spark_df = spark.createDataFrame(combined_pdf)
    
    # Write to Unity Catalog external tables
    merge_into_delta(spark_df, TARGET_TABLE)