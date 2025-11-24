import httpx
from typing import Optional, List
from .models import NormalizedLog, SemanticResult, IntentResult, MitreResult, RiskScore

# Shared Async Client
# We'll instantiate this in app startup or use a singleton pattern
async_client = httpx.AsyncClient()

def build_summary(
    normalized: Optional[NormalizedLog],
    semantic: Optional[SemanticResult],
    intent: Optional[IntentResult],
    mitre: Optional[MitreResult],
    risk: Optional[RiskScore],
) -> str:
    """
    Create a 1-2 sentence summary.
    """
    parts = []
    
    # Risk prefix
    if risk:
        parts.append(f"[{risk.level.upper()} RISK]")
    
    # Intent/Technique
    if intent and intent.intent != "unknown":
        parts.append(f"Potential {intent.intent.replace('_', ' ')}")
    elif mitre:
        parts.append(f"Potential {mitre.attack_technique}")
    else:
        parts.append("Suspicious activity")

    # Context
    if normalized:
        if normalized.user:
            parts.append(f"by user '{normalized.user}'")
        if normalized.hostname:
            parts.append(f"on host '{normalized.hostname}'")
    
    # Semantic summary as fallback or addition
    if semantic:
        parts.append(f"- {semantic.semantic_summary}")
        
    # MITRE ID
    if mitre:
        parts.append(f"({mitre.technique_id})")

    return " ".join(parts)

def build_recommendations(
    intent: Optional[IntentResult],
    mitre: Optional[MitreResult],
    risk: Optional[RiskScore],
) -> List[str]:
    """
    Return a short list of concrete SOC actions.
    """
    recs = []
    
    # High level risk actions
    if risk and risk.level in ["high", "critical"]:
        recs.append("IMMEDIATE ACTION: Isolate affected host from network.")
        recs.append("Escalate to Tier 2 analyst.")

    # Intent based
    if intent:
        if intent.intent == "credential_dumping":
            recs.append("Check for LSASS access or Mimikatz usage.")
            recs.append("Reset passwords for affected users.")
        elif intent.intent == "lateral_movement":
            recs.append("Review network logs for connections from source host.")
        elif intent.intent == "command_and_control":
            recs.append("Block destination IP/Domain at firewall.")

    # MITRE based
    if mitre:
        recs.append(f"Investigate usage of technique {mitre.technique_id} ({mitre.attack_technique}).")
        
    if not recs:
        recs.append("Review raw log and monitor for further suspicious activity.")

    return recs
