import os
import pandas as pd
from src.core.config import get_feature_list
from src.core.logger import logger
from src.data.spark_pipeline import get_spark_session
from src.data.databricks_client import DatabricksClient
from src.models.regression import StockPriceRegressor
from src.models.classification import StockClassifier

def run_training_pipeline() -> None:
    logger.info("Starting automated offline training pipeline...")
    
    spark = get_spark_session()
    db_client = DatabricksClient()

    indicators_df = db_client.read_dataset(spark, table_name="aapl_indicators").toPandas()
    sentiment_df = db_client.read_dataset(spark, table_name="aapl_sentiment").toPandas()

    indicators_df["date"] = pd.to_datetime(indicators_df["date"])
    sentiment_df["date"] = pd.to_datetime(sentiment_df["timestamp"]).dt.date
    sentiment_df["date"] = pd.to_datetime(sentiment_df["date"])

    daily_sentiment = (
        sentiment_df.groupby(["date", "ticker"])[
            ["neg_score", "neu_score", "pos_score", "compound_score"]
        ]
        .mean()
        .reset_index()
    )

    df = pd.merge(indicators_df, daily_sentiment, on=["date", "ticker"], how="left").fillna(0)
    df = df.sort_values("date").reset_index(drop=True)

    # Train Regressor
    regressor = StockPriceRegressor()
    X_reg, y_reg = regressor.prepare_data(df)
    regressor.train(X_reg, y_reg)
    regressor.save_model("models/regressor.joblib")

    # Train Classifiers
    classifier = StockClassifier()
    clf_df = classifier.prepare_data(df)
    
    feature_cols = get_feature_list()
    feature_cols = [c for c in feature_cols if c in clf_df.columns]
    
    X_clf = clf_df[feature_cols]
    y_dir = clf_df["target_direction"]
    y_strat = clf_df["target_strategy"]

    classifier.train_direction(X_clf, y_dir)
    classifier.train_strategy(X_clf, y_strat)
    classifier.save_models()

    logger.info("Automated training pipeline complete. Model binaries saved to models/")

if __name__ == "__main__":
    run_training_pipeline()