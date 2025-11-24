from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal

class SemanticInput(BaseModel):
    semantic_summary: str
    semantic_features: Dict[str, Any] = Field(
        ..., 
        description="Must contain keys like operation_type, resource_type, access_channel, direction, suspicious_indicators"
    )
    confidence: float

class IntentClassificationResult(BaseModel):
    intent: str
    tactic: str
    score: float
    matched_rules: List[str]
    source: Literal["rules", "llm"]
    explanation: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None

class Rule(BaseModel):
    id: str
    intent: str
    tactic: str
    description: str
    conditions: Dict[str, Any]
    weights: Dict[str, float]
