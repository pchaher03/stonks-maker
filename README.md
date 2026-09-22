# Stonks Maker

Repo: [https://github.com/pchaher03/stonks-maker](https://github.com/pchaher03/stonks-maker)

![stonks](https://static.wikia.nocookie.net/memes-pedia/images/d/df/Nada.png/revision/latest?cb=20201119214705&path-prefix=es)

## Objective

**Stonks Maker** is an end-to-end quantitative and data-driven software solution designed to help users make informed trading decisions in the stock market. It combines big data processing, financial sentiment analysis via NLP, machine learning predictions, and model interpretability (SHAP) wrapped in a high-performance FastAPI service.

---

## Functional Requirements

* **End-to-End FastAPI Application**: RESTful API endpoints serving real-time and batch predictions, news sentiment metrics, and model explanations.
* **Fully Containerized Infrastructure**: Single `docker-compose` environment orchestrating FastAPI, JupyterLab, PySpark, and Databricks integration.
* **Machine Learning Pipelines**:
  * **Price Prediction (Regression)**: Forecasts specific stock price values over target horizons.
  * **Movement Prediction (Classification)**: Predicts whether a stock price will go UP or DOWN.
  * **Strategy Suitability (Classification)**: Assesses market dynamics (volatility, momentum, volume) to evaluate whether a stock is suitable for **Day Trading** or **Swing Trading**.
* **Financial NLP**: Processes financial news and headlines to calculate sentiment scores used as model input features.
* **Model Explainability**: Integrates **SHAP** (SHapley Additive exPlanations) to explain individual predictions and feature importances.

---

## Technologies Used

* **FastAPI**: Asynchronous web framework for high-throughput model serving.
* **PySpark**: Scalable engine for big data feature engineering and batch transformations.
* **Databricks**: Cloud data management and Delta Lake storage integration.
* **Docker & Docker Compose**: Unified containerization for local development and reproducibility.
* **JupyterLab**: Interactive environment for Exploratory Data Analysis (EDA), feature prototyping, and model validation.
* **SHAP**: Explainable AI framework for feature attribution on model predictions.

---

## Repo Structure

```text
stonks-maker/
├── .github/                     # CI/CD workflows and automation
├── config/                      # Application & model configurations
│   ├── config.yaml              # Global settings (tickers, dates, DB paths)
│   └── model_params.yaml        # Hyperparameters for ML models
├── docker/                      # Dockerfiles for specific services
│   ├── Dockerfile.fastapi       # FastAPI service container
│   └── Dockerfile.jupyter       # Jupyter Lab environment with PySpark
├── docker-compose.yml           # Multi-container orchestration
├── notebooks/                   # Jupyter Notebooks for exploration
│   ├── 01_eda.ipynb             # Exploratory Data Analysis
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_evaluation.ipynb
├── src/                         # Core Python package
│   ├── __init__.py
│   ├── core/                    # Core app settings & logging
│   │   ├── config.py            # Pydantic BaseSettings parser
│   │   └── logger.py            # Standardized application logging
│   ├── data/                    # Data ingestion & Spark processing
│   │   ├── databricks_client.py # Databricks REST API / SDK helper
│   │   ├── ingestion.py         # Market data fetchers (Alpha Vantage, Yahoo)
│   │   └── spark_pipeline.py    # Spark aggregation & indicator pipelines
│   ├── nlp/                     # News & sentiment analysis
│   │   ├── news_fetcher.py      # Financial news feed fetcher
│   │   └── sentiment_analyzer.py# Sentiment scoring (FinBERT / VADER)
│   ├── models/                  # ML training, inference & explainability
│   │   ├── train.py             # Model training runner script
│   │   ├── regression.py        # Target price prediction model
│   │   ├── classification.py    # Direction & Strategy (Day/Swing) classifiers
│   │   └── explainability.py    # SHAP value calculator
│   └── api/                     # FastAPI Application
│       ├── main.py              # Application entrypoint
│       ├── dependencies.py      # Shared dependencies & model loaders
│       └── v1/
│           ├── endpoints/
│           │   ├── predictions.py # Inference routes
│           │   ├── news.py        # NLP / Sentiment routes
│           │   └── explain.py     # SHAP analysis routes
│           └── schemas/         # Pydantic response/request models
│               └── trading.py
├── tests/                       # Unit and integration test suites
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── .gitignore
├── .dockerignore
└── README.md
```

---

## Module Definitions

### 1. Core (`src/core/`)
* **`config.py`**: Manages environment variables, API keys, and global parameters using Pydantic settings.
* **`logger.py`**: Provides structured logging across all services.

### 2. Data Engineering (`src/data/`)
* **`ingestion.py`**: Connects to financial data APIs to pull OHLCV (Open, High, Low, Close, Volume) data.
* **`spark_pipeline.py`**: Uses PySpark to process high-volume historical data and compute technical indicators (RSI, MACD, Bollinger Bands, Moving Averages).
* **`databricks_client.py`**: Handles read/write operations to Databricks Delta Lake tables.

### 3. NLP Module (`src/nlp/`)
* **`news_fetcher.py`**: Scrapes or queries financial news feeds for ticker-specific news articles.
* **`sentiment_analyzer.py`**: Extracts sentiment polarity and intensity scores to supply temporal sentiment features to downstream models.

### 4. Machine Learning & Interpretability (`src/models/`)
* **`regression.py`**: Implements price target prediction algorithms.
* **`classification.py`**:
  * *Direction Classifier*: Outputs binary movement predictions (UP/DOWN).
  * *Strategy Classifier*: Analyzes market regimes (volatility, liquidity) to classify whether market conditions favor **Day Trading** or **Swing Trading**.
* **`explainability.py`**: Generates SHAP summary values and individual feature attributions for any given prediction.

### 5. API Layer (`src/api/`)
* **`main.py`**: Sets up FastAPI middleware, CORS policies, and includes API routers.
* **`endpoints/`**:
  * `/v1/predictions`: Exposes inference endpoints for price targets, movement, and strategy suitability.
  * `/v1/news`: Exposes sentiment analysis summaries for tickers.
  * `/v1/explain`: Serves calculated SHAP values and feature contribution breakdowns.
* **`schemas/trading.py`**: Defines strict type validation for API requests and JSON responses.

---

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pchaher03/stonks-maker.git
   cd stonks-maker
   ```

2. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Update .env with your Databricks tokens and API keys
   ```

3. **Launch Infrastructure via Docker Compose**:
   ```bash
   docker compose up --build
   ```

4. **Access Services**:
   * **FastAPI Docs**: `http://localhost:8000/docs`
   * **JupyterLab**: `http://localhost:8888`
   * **Spark UI**: `http://localhost:4040`

---

# Stonks Maker: Implementation Roadmap

## Phase 1: Core Foundation & Data Pipeline (The Data Backbone)
Before training models or spinning up API endpoints, you need clean, reproducible data flows.

1. **`src/core/config.py` & `logger.py`**
   * Set up Pydantic `BaseSettings` to parse `.env` (API keys, Databricks tokens, PySpark config).
   * Implement structured logging (e.g., via `structlog` or standard `logging`).

2. **Data Ingestion (`src/data/ingestion.py`)**
   * Build basic fetchers for market OHLCV data (e.g., `yfinance` or Alpha Vantage).
   * Implement caching to avoid hitting API rate limits during testing.

3. **Spark Transformations (`src/data/spark_pipeline.py`)**
   * Create PySpark job functions to calculate basic technical indicators:
     * Relative Strength Index (RSI)
     * Moving Average Convergence Divergence (MACD)
     * Bollinger Bands & Simple Moving Averages (SMA/EMA)
   * Verify that Spark transforms execute correctly locally before connecting to Databricks.

4. **Databricks Delta Lake Sync (`src/data/databricks_client.py`)**
   * Set up read/write wrappers to save transformed datasets into Delta Lake tables or local Parquet mock storage for offline dev.

---

## Phase 2: Financial NLP Pipeline
Isolate sentiment extraction so it can act as a feature engineering step for downstream ML.

1. **News Collector (`src/nlp/news_fetcher.py`)**
   * Connect to a news API (e.g., NewsAPI, Finviz scraper, or Yahoo Finance news).
   * Normalize output schema: `[timestamp, ticker, headline, text]`.

2. **Sentiment Scoring (`src/nlp/sentiment_analyzer.py`)**
   * Implement FinBERT (via Hugging Face `transformers`) or VADER for sentiment scoring.
   * *Performance Tip:* FinBERT can be compute-heavy. Ensure batch processing is supported when calculating historical sentiment features.
   * Output normalized scores: `[positive_score, negative_score, neutral_score, compound_score]`.

---

## Phase 3: Model Training & SHAP Explainability
With technical indicators and sentiment scores ready, move to interactive model prototyping.

1. **Jupyter Analysis (`notebooks/01_eda.ipynb` & `02_feature_engineering.ipynb`)**
   * Merge market technical indicators with NLP sentiment time-series data.
   * Handle data alignment issues (e.g., weekend news mapped to Monday market open).
   * Define target variables:
     * **Regression:** Future price ($t + n$).
     * **Direction:** Binary classification (1 if $Price_{t+n} > Price_t$, else 0).
     * **Strategy Suitability:** Label volatility/volume regimes (e.g., high intraday ATR + high volume $\rightarrow$ Day Trading).

2. **Model Implementation (`src/models/`)**
   * Write modular classes in `regression.py` and `classification.py` using XGBoost, LightGBM, or Scikit-Learn.
   * Implement model persistence (save/load pipelines via `joblib` or MLflow).

3. **Model Explainability (`src/models/explainability.py`)**
   * Build a utility class taking a trained model and feature vector, returning SHAP base values and feature contributions.

---

## Phase 4: API Layer & End-to-End Orchestration
Expose predictions and interpretations through FastAPI endpoints.

1. **Schemas (`src/api/v1/schemas/trading.py`)**
   * Define Pydantic request models (e.g., `PredictionRequest(ticker="AAPL", horizon="5d")`).
   * Define response models for predictions, sentiment, and SHAP feature importances.

2. **Dependencies (`src/api/dependencies.py`)**
   * Implement singleton pattern or application lifespan (`@asynccontextmanager`) to load trained ML models into memory once at startup rather than per request.

3. **Endpoints (`src/api/v1/endpoints/`)**
   * `/v1/predictions`: Execute inference using pre-loaded models.
   * `/v1/news`: Trigger news fetcher and sentiment analyzer for immediate ticker sentiment.
   * `/v1/explain`: Return SHAP feature attributions formatted for UI/JSON consumption.

4. **Docker Integration Validation**
   * Test the complete flow inside `docker-compose up`: ensure FastAPI can communicate with PySpark and read artifacts seamlessly.

---

## Key Technical Considerations

* **Lookahead Bias in Feature Engineering:** When calculating technical indicators or sentiment averages, ensure windows use strictly historical data relative to prediction time $t$.
* **FastAPI Model Loading:** Avoid calling heavy initialization routines inside route functions. Use FastAPI's `lifespan` context manager in `main.py` to keep models ready in memory.
* **Databricks Local Fallback:** Allow `databricks_client.py` to fall back to local file storage (Parquet/SQLite) when running offline or without active cloud credentials.