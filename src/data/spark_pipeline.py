from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from src.core.logger import logger

def get_spark_session(app_name: str = "StonksSparkPipeline") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )

class SparkTechnicalIndicators:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def compute_indicators(self, df: DataFrame) -> DataFrame:
        logger.info("Starting Spark indicator transformations...")
        
        # Define window specs ordered by date per ticker
        window_spec = Window.partitionBy("ticker").orderBy("date")
        
        # 1. Simple Moving Averages (SMA)
        df = df.withColumn("sma_20", F.avg("close").over(window_spec.rowsBetween(-19, 0)))
        df = df.withColumn("sma_50", F.avg("close").over(window_spec.rowsBetween(-49, 0)))

        # 2. Bollinger Bands (20-day)
        std_20 = F.stddev("close").over(window_spec.rowsBetween(-19, 0))
        df = df.withColumn("bollinger_upper", F.col("sma_20") + (std_20 * 2))
        df = df.withColumn("bollinger_lower", F.col("sma_20") - (std_20 * 2))

        # 3. Daily Price Change & RSI Calculation
        df = df.withColumn("prev_close", F.lag("close", 1).over(window_spec))
        df = df.withColumn("change", F.col("close") - F.col("prev_close"))
        df = df.withColumn("gain", F.when(F.col("change") > 0, F.col("change")).otherwise(0))
        df = df.withColumn("loss", F.when(F.col("change") < 0, -F.col("change")).otherwise(0))

        # 14-period Average Gain / Loss for RSI
        avg_gain_14 = F.avg("gain").over(window_spec.rowsBetween(-13, 0))
        avg_loss_14 = F.avg("loss").over(window_spec.rowsBetween(-13, 0))
        rs = avg_gain_14 / (avg_loss_14 + 1e-6)
        df = df.withColumn("rsi_14", 100 - (100 / (1 + rs)))

        # Clean intermediate columns
        df = df.drop("prev_close", "change", "gain", "loss")
        logger.info("Completed Spark indicator calculations.")
        return df