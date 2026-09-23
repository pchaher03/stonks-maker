import os
import joblib
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.core.logger import logger

class StockPriceRegressor:
    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.05, max_depth: int = 5, random_state: int = 42):
        self.model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state
        )
        self.feature_names = []

    def prepare_data(self, df: pd.DataFrame, target_horizon: int = 1) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Creates the target variable (future price at t + horizon) and removes null rows.
        """
        df = df.sort_values("date").copy()
        df["target_price"] = df.groupby("ticker")["close"].shift(-target_horizon)
        
        # Select numeric feature columns
        feature_cols = [
            c for c in df.columns 
            if c not in ["date", "ticker", "target_price"] and pd.api.types.is_numeric_dtype(df[c])
        ]
        
        clean_df = df.dropna(subset=feature_cols + ["target_price"]).reset_index(drop=True)
        self.feature_names = feature_cols
        
        return clean_df[feature_cols], clean_df["target_price"]

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        logger.info("Training Stock Price Regressor...")
        self.model.fit(X_train, y_train)
        logger.info("Regressor training completed.")

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        predictions = self.model.predict(X_test)
        metrics = {
            "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
            "mae": float(mean_absolute_error(y_test, predictions)),
            "r2": float(r2_score(y_test, predictions))
        }
        logger.info(f"Regression Evaluation Metrics: {metrics}")
        return metrics

    def save_model(self, path: str = "models/regressor.joblib") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({"model": self.model, "features": self.feature_names}, path)
        logger.info(f"Regressor saved to {path}")

    def load_model(self, path: str = "models/regressor.joblib") -> None:
        data = joblib.load(path)
        self.model = data["model"]
        self.feature_names = data["features"]
        logger.info(f"Regressor loaded from {path}")