from contextlib import asynccontextmanager
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.logger import logger
from src.api.v1.endpoints import predictions, news, explain

# Application lifespan context manager to load models into memory at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Stonks Maker API service...")
    # Verify pre-trained models exist or pre-load shared resources if needed
    try:
        reg_data = joblib.load("models/regressor.joblib")
        logger.info("Regressor model verified and ready.")
    except Exception as e:
        logger.warning(f"Could not pre-load regression model at startup: {e}")
    
    yield
    
    logger.info("Shutting down Stonks Maker API service...")

app = FastAPI(
    title="Stonks Maker API",
    description="Quantitative Trading Prediction & Explainability Microservice",
    version="1.0.0",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Phase 4 endpoint routers
app.include_router(predictions.router, prefix="/v1", tags=["Predictions"])
app.include_router(news.router, prefix="/v1", tags=["Sentiment"])
app.include_router(explain.router, prefix="/v1", tags=["Explainability"])

@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Stonks Maker API is running!"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Stonks Maker API"}