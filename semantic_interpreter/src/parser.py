from pydantic import BaseModel, Field
from typing import Dict, Any

class LogAnalysis(BaseModel):
    semantic_summary: str
    semantic_features: Dict[str, Any]
    confidence: float
