from typing import Optional, Dict, Any
from .models import SemanticResult, IntentResult, MitreResult, RiskScore

def compute_risk(
    semantic: Optional[SemanticResult],
    intent: Optional[IntentResult],
    mitre: Optional[MitreResult],
) -> RiskScore:
    """
    Combine available confidences into a single 0-1 risk score.
    """
    score = 0.0
    factors: Dict[str, Any] = {}

    # 1. Semantic Confidence (Base)
    if semantic:
        # Semantic confidence usually reflects how "bad" the log looks
        # We weight it by 0.3
        s_conf = semantic.confidence
        score += 0.3 * s_conf
        factors["semantic"] = f"Confidence {s_conf:.2f} (+{0.3 * s_conf:.2f})"

    # 2. Intent Score (Strong indicator)
    if intent:
        # Intent score comes from rules or LLM
        # We weight it by 0.4
        i_score = intent.score
        score += 0.4 * i_score
        factors["intent"] = f"Intent '{intent.intent}' score {i_score:.2f} (+{0.4 * i_score:.2f})"
        
        # Bonus for high severity intents
        if intent.intent in ["credential_dumping", "ransomware_deployment", "data_exfiltration"]:
            score += 0.1
            factors["intent_severity_bonus"] = "+0.1 (Critical Intent)"

    # 3. MITRE Confidence
    if mitre:
        # MITRE confidence
        # We weight it by 0.2
        m_conf = mitre.confidence
        score += 0.2 * m_conf
        factors["mitre"] = f"Technique {mitre.technique_id} confidence {m_conf:.2f} (+{0.2 * m_conf:.2f})"

    # Cap score at 1.0
    score = min(score, 1.0)

    # Determine Level
    if score < 0.3:
        level = "low"
    elif score < 0.6:
        level = "medium"
    elif score < 0.8:
        level = "high"
    else:
        level = "critical"

    return RiskScore(score=score, level=level, factors=factors)
