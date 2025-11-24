import httpx
from typing import Optional
from ..models import NormalizedLog, SemanticResult
from ..config import settings
from ..logger import logger
from ..utils import async_client

async def call_semantic_interpreter(normalized: NormalizedLog, correlation_id: str) -> Optional[SemanticResult]:
    """
    POST {SEMANTIC_URL}/interpret
    """
    url = f"{settings.SEMANTIC_URL}/interpret"
    
    # Semantic Interpreter expects: { "raw_log": "...", "fields": {...} }
    payload = {
        "raw_log": normalized.raw_log,
        "fields": normalized.normalized_fields
    }

    try:
        logger.info(f"Calling Semantic Interpreter: {url}", extra={"correlation_id": correlation_id})
        response = await async_client.post(
            url, 
            json=payload, 
            timeout=settings.ORCHESTRATOR_TIMEOUT,
            headers={"X-Correlation-ID": correlation_id}
        )
        response.raise_for_status()
        return SemanticResult(**response.json())
    except Exception as e:
        logger.error(f"Semantic Interpreter failed: {e}", extra={"correlation_id": correlation_id})
        return None
