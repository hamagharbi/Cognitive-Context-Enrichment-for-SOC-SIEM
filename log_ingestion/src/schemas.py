from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class IngestRequest(BaseModel):
    raw_log: str
    fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    source_type: Optional[str] = None  # Optional hint

class NormalizedEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    event_type: str
    hostname: Optional[str] = None
    user: Optional[str] = None
    message: str
    raw_log: str
    normalized_fields: Dict[str, Any] = Field(default_factory=dict)
