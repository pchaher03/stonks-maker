import shap
import pandas as pd
import numpy as np
from typing import Dict, Any
from src.core.logger import logger

class ModelExplainer:
    def __init__(self, model: Any, feature_names: list):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(self.model)

    def explain_instance(self, instance_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes SHAP values for a single input feature vector.
        """
        if instance_df.empty:
            return {"error": "Empty dataframe provided."}
            
        instance_features = instance_df[self.feature_names]
        shap_values = self.explainer.shap_values(instance_features)
        
        # Extract 1D array of feature contributions
        if isinstance(shap_values, list):
            vals = shap_values[0]
        else:
            vals = shap_values
            
        if vals.ndim == 2:
            vals = vals[0]
            
        contributions = {
            feature: float(val) 
            for feature, val in zip(self.feature_names, vals)
        }
        
        # Extract scalar base value safely
        base_val = self.explainer.expected_value
        if isinstance(base_val, (list, np.ndarray)):
            base_val = float(base_val[0])
        else:
            base_val = float(base_val)
        
        return {
            "base_value": base_val,
            "feature_contributions": contributions
        }