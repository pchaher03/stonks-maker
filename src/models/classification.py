import os
import joblib
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from src.core.logger import logger

class StockClassifier:
    def __init__(self, n_estimators: int = 100, max_depth: int = 4, random_state: int = 42):
        self.direction_model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)
        self.strategy_model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)
        self.feature_names = []

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values("date").copy()
        
        # Target 1: Direction (1 if future close > current close, else 0)
        df["future_close"] = df.groupby("ticker")["close"].shift(-1)
        df["target_direction"] = (df["future_close"] > df["close"]).astype(int)
        
        # Target 2: Strategy Suitability (High ATR/Volatility -> Day Trading, Else Swing Trading)
        # Using normalized intraday price spread as proxy for volatility
        volatility = (df["high"] - df["low"]) / df["close"]
        df["target_strategy"] = np.where(volatility > volatility.median(), "Day Trading", "Swing Trading")
        
        return df.dropna(subset=["future_close"])

    def train_direction(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        logger.info("Training Movement Direction Classifier (UP/DOWN)...")
        self.feature_names = X_train.columns.tolist()
        self.direction_model.fit(X_train, y_train)

    def train_strategy(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        logger.info("Training Strategy Classifier (Day vs Swing)...")
        self.strategy_model.fit(X_train, y_train)

    def evaluate(self, X_test: pd.DataFrame, y_dir_test: pd.Series, y_strat_test: pd.Series) -> Dict[str, Any]:
        dir_preds = self.direction_model.predict(X_test)
        strat_preds = self.strategy_model.predict(X_test)
        
        metrics = {
            "direction_accuracy": float(accuracy_score(y_dir_test, dir_preds)),
            "direction_f1": float(f1_score(y_dir_test, dir_preds, average="weighted")),
            "strategy_accuracy": float(accuracy_score(y_strat_test, strat_preds)),
            "strategy_f1": float(f1_score(y_strat_test, strat_preds, average="weighted"))
        }
        logger.info(f"Classification Metrics: {metrics}")
        return metrics

    def save_models(self, path_dir: str = "models/direction_clf.joblib", path_strat: str = "models/strategy_clf.joblib") -> None:
        os.makedirs(os.path.dirname(path_dir), exist_ok=True)
        joblib.dump({"model": self.direction_model, "features": self.feature_names}, path_dir)
        joblib.dump({"model": self.strategy_model, "features": self.feature_names}, path_strat)
        logger.info("Classifier models saved successfully.")