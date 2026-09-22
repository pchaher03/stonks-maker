import shap
import pandas as pd
import numpy as np
from typing import Dict, Any
from src.core.logger import logger

class ModelExplainer:
    def __init__(self, model: Any, feature_names: list):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.Explainer(self.model)

    def explain_instance(self, instance_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes SHAP values for a single input feature vector.
        """
        if instance_df.empty:
            return {"error": "Empty dataframe provided."}
            
        instance_features = instance_df[self.feature_names]
        shap_values = self.explainer(instance_features)
        
        # Format outputs as serializable dictionary
        vals = shap_values.values[0]
        if len(vals.shape) > 1:  # Handle multi-class outputs
            vals = vals[:, 1]
            
        contributions = dict(zip(self.feature_names, [float(v) for v in vals]))
        
        return {
            "base_value": float(shap_values.base_values[0] if isinstance(shap_values.base_values, np.ndarray) else shap_values.base_values),
            "feature_contributions": contributions
        }