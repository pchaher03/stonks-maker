import os
import joblib
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from src.core.config import get_model_params, get_feature_list
from src.core.logger import logger

class StockClassifier:
    def __init__(
        self, 
        n_estimators: Optional[int] = None, 
        max_depth: Optional[int] = None, 
        random_state: Optional[int] = None
    ):
        clf_params = get_model_params().get("models", {}).get("classification", {})
        dir_params = clf_params.get("direction", {})
        strat_params = clf_params.get("strategy", {})

        dir_n_est = n_estimators if n_estimators is not None else dir_params.get("n_estimators", 100)
        dir_depth = max_depth if max_depth is not None else dir_params.get("max_depth", 4)
        dir_rs = random_state if random_state is not None else dir_params.get("random_state", 42)

        strat_n_est = n_estimators if n_estimators is not None else strat_params.get("n_estimators", 100)
        strat_depth = max_depth if max_depth is not None else strat_params.get("max_depth", 4)
        strat_rs = random_state if random_state is not None else strat_params.get("random_state", 42)

        self.direction_model = RandomForestClassifier(
            n_estimators=dir_n_est, max_depth=dir_depth, random_state=dir_rs
        )
        self.strategy_model = RandomForestClassifier(
            n_estimators=strat_n_est, max_depth=strat_depth, random_state=strat_rs
        )
        self.feature_names = []

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values("date").copy()
        
        # Target 1: Direction (1 if future close > current close, else 0)
        df["future_close"] = df.groupby("ticker")["close"].shift(-1)
        df["target_direction"] = (df["future_close"] > df["close"]).astype(int)
        
        # Target 2: Strategy Suitability (High ATR/Volatility -> Day Trading, Else Swing Trading)
        volatility = (df["high"] - df["low"]) / df["close"]
        df["target_strategy"] = np.where(volatility > volatility.median(), "Day Trading", "Swing Trading")
        
        return df.dropna(subset=["future_close"])

    def train_direction(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        logger.info("Training Movement Direction Classifier (UP/DOWN)...")
        configured_features = get_feature_list()
        self.feature_names = [c for c in configured_features if c in X_train.columns] or X_train.columns.tolist()
        self.direction_model.fit(X_train[self.feature_names], y_train)

    def train_strategy(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        logger.info("Training Strategy Classifier (Day vs Swing)...")
        configured_features = get_feature_list()
        features = [c for c in configured_features if c in X_train.columns] or X_train.columns.tolist()
        self.strategy_model.fit(X_train[features], y_train)

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

    def save_models(
        self, 
        path_dir: str = "models/direction_clf.joblib", 
        path_strat: str = "models/strategy_clf.joblib"
    ) -> None:
        os.makedirs(os.path.dirname(path_dir), exist_ok=True)
        joblib.dump({"model": self.direction_model, "features": self.feature_names}, path_dir)
        joblib.dump({"model": self.strategy_model, "features": self.feature_names}, path_strat)
        logger.info("Classifier models saved successfully.")

    def load_models(
        self, 
        path_dir: str = "models/direction_clf.joblib", 
        path_strat: str = "models/strategy_clf.joblib"
    ) -> None:
        data_dir = joblib.load(path_dir)
        data_strat = joblib.load(path_strat)
        self.direction_model = data_dir["model"]
        self.strategy_model = data_strat["model"]
        self.feature_names = data_dir["features"]
        logger.info("Classifier models loaded successfully.")