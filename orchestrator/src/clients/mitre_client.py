import httpx
from typing import Optional
from ..models import SemanticResult, IntentResult, MitreResult
from ..config import settings
from ..logger import logger
from ..utils import async_client

async def call_mitre_reasoner(
    semantic: SemanticResult,
    intent: Optional[IntentResult],
    correlation_id: str,
    k: int = 5,
) -> Optional[MitreResult]:
    """
    POST {MITRE_URL}/analyze
    """
    url = f"{settings.MITRE_URL}/analyze"
    
    # MITRE Reasoner expects:
    # { "semantic_summary": "...", "semantic_features": {...}, "intent": "...", "k": 5 }
    payload = {
        "semantic_summary": semantic.semantic_summary,
        "semantic_features": semantic.semantic_features,
        "intent": intent.intent if intent else "unknown",
        "k": k
    }

    try:
        logger.info(f"Calling MITRE Reasoner: {url}", extra={"correlation_id": correlation_id})
        response = await async_client.post(
            url, 
            json=payload, 
            timeout=settings.ORCHESTRATOR_TIMEOUT,
            headers={"X-Correlation-ID": correlation_id}
        )
        response.raise_for_status()
        return MitreResult(**response.json())
    except Exception as e:
        logger.error(f"MITRE Reasoner failed: {e}", extra={"correlation_id": correlation_id})
        return None
