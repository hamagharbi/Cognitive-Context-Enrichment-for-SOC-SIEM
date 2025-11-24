from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

class SemanticAnalysisRequest(BaseModel):
    semantic_summary: str
    semantic_features: Union[List[str], Dict[str, Any]]
    intent: str
    k: Optional[int] = 5

class MitreTechnique(BaseModel):
    technique_id: Optional[str] = None
    name: str
    description: str
    url: Optional[str] = None
    score: float
    source: str

    tactic: Optional[str] = None
    kill_chain_phase: Optional[str] = None
    subtechnique_of: Optional[str] = None


class MitreTechniqueResponse(BaseModel):
    attack_technique: str
    technique_id: str
    tactic: str
    kill_chain_phase: str
    confidence: float
    explanation: str
    related_techniques: List[str]
