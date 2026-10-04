from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class PredictionRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    horizon: Optional[int] = Field(default=1, description="Prediction horizon in days")

class PredictionResponse(BaseModel):
    ticker: str
    company_name: Optional[str] = None
    current_price: float
    target_price: float
    direction: str
    recommended_strategy: str

class ArticleItem(BaseModel):
    title: str
    source: Optional[str] = "Financial News"
    timestamp: Optional[str] = None
    url: Optional[str] = "#"
    compound_score: Optional[float] = 0.0

class SentimentResponse(BaseModel):
    ticker: str
    compound_score: float
    pos_score: float
    neg_score: float
    neu_score: float
    articles: Optional[List[ArticleItem]] = []

class ExplanationResponse(BaseModel):
    ticker: str
    base_value: float
    feature_contributions: Dict[str, float]