import httpx
from typing import Optional
from ..models import RawLogRequest, NormalizedLog
from ..config import settings
from ..logger import logger
from ..utils import async_client

async def call_log_ingestion(raw: RawLogRequest, correlation_id: str) -> Optional[NormalizedLog]:
    """
    POST {LOG_INGEST_URL}/ingest
    """
    url = f"{settings.LOG_INGEST_URL}/ingest"
    
    # Map RawLogRequest to what Log Ingestion expects
    # Log Ingestion expects: { "raw_log": "...", "fields": {}, "source_type": "..." }
    payload = {
        "raw_log": raw.raw_log,
        "fields": raw.metadata,
        "source_type": raw.source
    }

    try:
        logger.info(f"Calling Log Ingestion: {url}", extra={"correlation_id": correlation_id})
        response = await async_client.post(
            url, 
            json=payload, 
            timeout=settings.ORCHESTRATOR_TIMEOUT,
            headers={"X-Correlation-ID": correlation_id}
        )
        response.raise_for_status()
        return NormalizedLog(**response.json())
    except Exception as e:
        logger.error(f"Log Ingestion failed: {e}", extra={"correlation_id": correlation_id})
        return None
