import os
from pyspark.sql import DataFrame
from src.core.config import settings
from src.core.logger import logger

class DatabricksClient:
    def __init__(self):
        self.host = settings.DATABRICKS_HOST
        self.token = settings.DATABRICKS_TOKEN
        self.is_configured = bool(self.host and "your-databricks" not in self.host and self.token)
        
        # Resolve project root dynamically (/home/jovyan/work)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    def _resolve_path(self, relative_path: str) -> str:
        """Helper to ensure paths resolve inside project root rather than system root."""
        if os.path.isabs(relative_path):
            return relative_path
        return os.path.join(self.project_root, relative_path)

    def write_dataset(self, df: DataFrame, table_name: str, local_backup_path: str = "data/processed"):
        """
        Writes PySpark DataFrame to Databricks Delta table or local Parquet fallback.
        """
        if self.is_configured:
            logger.info(f"Databricks configured. Writing to Delta table: {table_name}")
            df.write.format("delta").mode("overwrite").saveAsTable(table_name)
        else:
            abs_backup_path = self._resolve_path(local_backup_path)
            output_dir = os.path.join(abs_backup_path, table_name)
            logger.info("Databricks credentials not configured. Saving locally to Parquet.")
            os.makedirs(abs_backup_path, exist_ok=True)
            df.write.mode("overwrite").parquet(output_dir)
            logger.info(f"Successfully saved to {output_dir}")

    def read_dataset(self, spark, table_name: str, local_backup_path: str = "data/processed") -> DataFrame:
        if self.is_configured:
            logger.info(f"Reading {table_name} from Databricks Delta Lake.")
            return spark.read.table(table_name)
        else:
            abs_backup_path = self._resolve_path(local_backup_path)
            output_dir = os.path.join(abs_backup_path, table_name)
            logger.info(f"Reading dataset locally from {output_dir}")
            return spark.read.parquet(output_dir)