from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime

# --- Input ---
class RawLogRequest(BaseModel):
    raw_log: str = Field(..., description="Original log line or message.")
    source: Optional[str] = Field(None, description="Source system, e.g. 'windows_eventlog', 'syslog', 'cloudtrail'.", alias="source_type")
    event_type: Optional[str] = Field(None, description="Optional type/category of event.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional extra context (tenant, tags, etc.).", alias="fields")

    class Config:
        populate_by_name = True

# --- Intermediate Results ---
class NormalizedLog(BaseModel):
    timestamp: datetime
    source: str
    event_type: str
    hostname: Optional[str] = None
    user: Optional[str] = None
    message: Optional[str] = None
    raw_log: str
    normalized_fields: Dict[str, Any]

class SemanticResult(BaseModel):
    semantic_summary: str
    semantic_features: Dict[str, Any]
    confidence: float

class IntentResult(BaseModel):
    intent: str
    tactic: str
    score: float
    matched_rules: List[str]
    source: Literal["rules", "llm"]
    explanation: Optional[str] = None

class MitreResult(BaseModel):
    attack_technique: str
    technique_id: str
    tactic: str
    kill_chain_phase: str
    confidence: float
    explanation: str
    related_techniques: List[str]

# --- Output ---
class RiskScore(BaseModel):
    score: float = Field(..., description="Risk score between 0.0 and 1.0")
    level: Literal["low", "medium", "high", "critical"]
    factors: Dict[str, Any] = Field(..., description="Explanation of how score was built")

class EnrichedAlert(BaseModel):
    correlation_id: str
    raw_log: str
    source: str
    event_type: Optional[str] = None

    normalized: Optional[NormalizedLog] = None
    semantic: Optional[SemanticResult] = None
    intent: Optional[IntentResult] = None
    mitre: Optional[MitreResult] = None

    risk: Optional[RiskScore] = None

    summary: Optional[str] = Field(
        None,
        description="1-2 line human-readable explanation for analysts."
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Concrete next steps for the SOC analyst."
    )

    errors: List[str] = Field(
        default_factory=list,
        description="Non-fatal errors encountered while calling downstream services."
    )
