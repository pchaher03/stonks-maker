import os
import joblib
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.core.config import get_model_params, get_feature_list
from src.core.logger import logger

class StockPriceRegressor:
    def __init__(
        self, 
        max_iter: Optional[int] = None, 
        learning_rate: Optional[float] = None, 
        max_depth: Optional[int] = None, 
        random_state: Optional[int] = None
    ):
        params = get_model_params().get("models", {}).get("regression", {})
        
        max_iter = max_iter if max_iter is not None else params.get("max_iter", 150)
        learning_rate = learning_rate if learning_rate is not None else params.get("learning_rate", 0.03)
        max_depth = max_depth if max_depth is not None else params.get("max_depth", 4)
        random_state = random_state if random_state is not None else params.get("random_state", 42)

        self.model = HistGradientBoostingRegressor(
            max_iter=max_iter,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state
        )
        self.feature_names = []

    def prepare_data(self, df: pd.DataFrame, target_horizon: int = 1) -> Tuple[pd.DataFrame, pd.Series]:
        """Calculates percentage return target and isolates features defined in config/model_params.yaml."""
        df = df.sort_values("date").copy()
        
        df["target_return"] = (df.groupby("ticker")["close"].shift(-target_horizon) - df["close"]) / df["close"]
        
        configured_features = get_feature_list()
        feature_cols = [c for c in configured_features if c in df.columns]
        
        if not feature_cols:
            feature_cols = [
                c for c in df.columns 
                if c not in ["date", "ticker", "target_price", "target_return"] and pd.api.types.is_numeric_dtype(df[c])
            ]
        
        clean_df = df.dropna(subset=feature_cols + ["target_return"]).reset_index(drop=True)
        self.feature_names = feature_cols
        
        return clean_df[feature_cols], clean_df["target_return"]

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        logger.info("Training Stock Price Regressor...")
        self.model.fit(X_train, y_train)
        logger.info("Regressor training completed.")

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        predictions = self.model.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
        mae = float(mean_absolute_error(y_test, predictions))
        r2 = float(r2_score(y_test, predictions))
        
        metrics = {"rmse": rmse, "mae": mae, "r2": r2}
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