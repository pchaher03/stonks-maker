import requests
import pandas as pd
import yfinance as yf
from delta.tables import DeltaTable

# Fetch the NewsAPI key from the Azure Key Vault-backed secret scope
API_KEY = dbutils.secrets.get(scope="stonks_secrets", key="news-api-key")
TARGET_TABLE = "stonks_catalog.bronze.raw_news"

def fetch_yfinance_news_fallback(ticker: str, limit: int = 20) -> pd.DataFrame:
    """Fallback method to fetch news via yfinance."""
    print(f"Fetching news for {ticker} via yfinance fallback...")
    try:
        yf_ticker = yf.Ticker(ticker)
        news_data = yf_ticker.news or []
        articles = []

        for item in news_data[:limit]:
            content = item.get("content", {}) if isinstance(item.get("content"), dict) else item
            title = content.get("title") or item.get("title", "")
            summary = content.get("summary") or item.get("summary", "")
            pub_time = content.get("pubDate") or item.get("providerPublishTime")

            provider_info = content.get("provider", {}) if isinstance(content.get("provider"), dict) else {}
            publisher = provider_info.get("displayName") or item.get("publisher") or "yfinance"

            articles.append({
                "timestamp": pd.to_datetime(pub_time, unit="s" if isinstance(pub_time, (int, float)) else None),
                "ticker": ticker,
                "title": title,
                "text": f"{title}. {summary}".strip(),
                "source": publisher
            })

        df = pd.DataFrame(articles)
        if not df.empty:
            return df[["timestamp", "ticker", "title", "text", "source"]]
    except Exception as e:
        print(f"Failed to parse yfinance news for {ticker} ({e}).")

    return pd.DataFrame(columns=["timestamp", "ticker", "title", "text", "source"])

def fetch_ticker_news(ticker: str, limit: int = 20) -> pd.DataFrame:
    """Fetches news from NewsAPI, falls back to yfinance on failure."""
    ticker = ticker.upper().strip()
    
    if API_KEY and "your_" not in API_KEY and len(API_KEY.strip()) > 0:
        try:
            print(f"Fetching news for {ticker} via NewsAPI...")
            url = (
                f"https://newsapi.org/v2/everything?"
                f"q={ticker}&sortBy=publishedAt&pageSize={limit}&apiKey={API_KEY}"
            )
            res = requests.get(url, timeout=10)
            
            if res.status_code == 200 and res.text.strip():
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
            print(f"NewsAPI request failed ({e}). Falling back to yfinance.")

    return fetch_yfinance_news_fallback(ticker, limit)

def merge_into_delta(spark_df, table_name: str):
    """
    Upserts new articles into the Delta table.
    """
    if spark.catalog.tableExists(table_name):
        print(f"Table {table_name} exists. Performing Delta MERGE for news...")
        delta_table = DeltaTable.forName(spark, table_name)
        
        # Match on a composite key to prevent duplicating articles.
        # News articles don't have perfect primary keys, so we match on ticker, time, and title.
        (delta_table.alias("target")
         .merge(
             source=spark_df.alias("source"),
             condition="""
                target.ticker = source.ticker 
                AND target.timestamp = source.timestamp 
                AND target.title = source.title
             """
         )
         # We only append new articles. No need for .whenMatchedUpdateAll() 
         # since historical news text doesn't change.
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
    tickers_to_update = ["AAPL", "NVDA", "TSLA"]
    
    all_news = []
    for ticker in tickers_to_update:
        pdf = fetch_ticker_news(ticker, limit=100)
        if not pdf.empty:
            all_news.append(pdf)
        
    if all_news:
        combined_pdf = pd.concat(all_news, ignore_index=True)
        # Convert pandas DataFrame to Spark DataFrame
        spark_df = spark.createDataFrame(combined_pdf)
        
        # Write to Unity Catalog external tables
        merge_into_delta(spark_df, TARGET_TABLE)
    else:
        print("No news data retrieved for any tickers.")