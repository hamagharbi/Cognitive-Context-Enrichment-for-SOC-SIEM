import httpx
from typing import Optional
from ..models import SemanticResult, IntentResult
from ..config import settings
from ..logger import logger
from ..utils import async_client

async def call_intent_classifier(semantic: SemanticResult, correlation_id: str) -> Optional[IntentResult]:
    """
    POST {INTENT_URL}/classify_intent
    """
    url = f"{settings.INTENT_URL}/classify_intent"
    
    # Intent Classifier expects SemanticInput: 
    # { "semantic_summary": "...", "semantic_features": {...}, "confidence": ... }
    payload = {
        "semantic_summary": semantic.semantic_summary,
        "semantic_features": semantic.semantic_features,
        "confidence": semantic.confidence
    }

    try:
        logger.info(f"Calling Intent Classifier: {url}", extra={"correlation_id": correlation_id})
        response = await async_client.post(
            url, 
            json=payload, 
            timeout=settings.ORCHESTRATOR_TIMEOUT,
            headers={"X-Correlation-ID": correlation_id}
        )
        response.raise_for_status()
        return IntentResult(**response.json())
    except Exception as e:
        logger.error(f"Intent Classifier failed: {e}", extra={"correlation_id": correlation_id})
        return None
