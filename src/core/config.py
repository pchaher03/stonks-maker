import os
from pydantic_settings import BaseSettings, SettingsConfigDict

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