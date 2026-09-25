import os
import yaml
from typing import Dict, Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve absolute path to project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CONFIG_YAML_PATH = os.path.join(PROJECT_ROOT, "config", "model_params.yaml")
APP_CONFIG_YAML_PATH = os.path.join(PROJECT_ROOT, "config", "config.yaml")

class Settings(BaseSettings):
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    API_PORT: int = 8000
    JUPYTER_PORT: int = 8888

    # Databricks Credentials
    DATABRICKS_HOST: str = ""
    DATABRICKS_TOKEN: str = ""
    DATABRICKS_HTTP_PATH: str = ""

    # External APIs
    ALPHA_VANTAGE_API_KEY: str = ""
    NEWS_API_KEY: str = ""

    # Spark Configuration
    SPARK_WORKER_MEMORY: str = "2G"
    SPARK_WORKER_CORES: int = 2

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()

def get_model_params() -> Dict[str, Any]:
    """Reads model hyperparameters and feature definitions from config/model_params.yaml."""
    if not os.path.exists(CONFIG_YAML_PATH):
        return {}
    with open(CONFIG_YAML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def get_feature_list() -> List[str]:
    """Extracts combined technical and sentiment feature column names from config/model_params.yaml."""
    params = get_model_params()
    features_cfg = params.get("features", {})
    tech = features_cfg.get("technical", [])
    senti = features_cfg.get("sentiment", [])
    return tech + senti

def get_default_tickers() -> List[str]:
    """Reads standard default ticker list from config/config.yaml."""
    if not os.path.exists(APP_CONFIG_YAML_PATH):
        return ["AAPL"]
    with open(APP_CONFIG_YAML_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg.get("app", {}).get("default_tickers", ["AAPL"])