import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .models import RawLogRequest, EnrichedAlert
from .config import settings
from .logger import logger
from .utils import async_client, build_summary, build_recommendations
from .scoring import compute_risk

from .clients.ingestion_client import call_log_ingestion
from .clients.semantic_client import call_semantic_interpreter
from .clients.intent_client import call_intent_classifier
from .clients.mitre_client import call_mitre_reasoner

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Enrichment Orchestrator starting up...")
    yield
    # Shutdown
    logger.info("Enrichment Orchestrator shutting down...")
    await async_client.aclose()

app = FastAPI(title="Enrichment Orchestrator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "config": {
            "ingest_url": settings.LOG_INGEST_URL,
            "semantic_url": settings.SEMANTIC_URL,
            "intent_url": settings.INTENT_URL,
            "mitre_url": settings.MITRE_URL
        }
    }

@app.post("/enrich_log", response_model=EnrichedAlert)
async def enrich_log(payload: RawLogRequest, request: Request):
    correlation_id = str(uuid.uuid4())
    logger.info(f"Starting enrichment for log source '{payload.source}'", extra={"correlation_id": correlation_id})
    
    errors = []

    # 1. Log Ingestion & Normalization (Critical Step)
    normalized = await call_log_ingestion(payload, correlation_id)
    if not normalized:
        logger.error("Ingestion failed. Aborting enrichment.", extra={"correlation_id": correlation_id})
        raise HTTPException(status_code=502, detail="Log Ingestion service failed or returned invalid data.")

    # 2. Semantic Interpretation
    semantic = await call_semantic_interpreter(normalized, correlation_id)
    if not semantic:
        errors.append("Semantic Interpreter failed")
    
    # 3. Intent Classification (Requires Semantic)
    intent = None
    if semantic:
        intent = await call_intent_classifier(semantic, correlation_id)
        if not intent:
            errors.append("Intent Classifier failed")
    else:
        errors.append("Skipped Intent Classifier (dependency missing)")

    # 4. MITRE Reasoning (Requires Semantic)
    mitre = None
    if semantic:
        mitre = await call_mitre_reasoner(semantic, intent, correlation_id)
        if not mitre:
            errors.append("MITRE Reasoner failed")
    else:
        errors.append("Skipped MITRE Reasoner (dependency missing)")

    # 5. Risk Scoring
    risk = compute_risk(semantic, intent, mitre)

    # 6. Summary & Recommendations
    summary = build_summary(normalized, semantic, intent, mitre, risk)
    recommendations = build_recommendations(intent, mitre, risk)

    # 7. Construct Final Alert
    # Use normalized source if payload source is missing
    final_source = payload.source or (normalized.source if normalized else "unknown")
    
    alert = EnrichedAlert(
        correlation_id=correlation_id,
        raw_log=payload.raw_log,
        source=final_source,
        event_type=payload.event_type,
        normalized=normalized,
        semantic=semantic,
        intent=intent,
        mitre=mitre,
        risk=risk,
        summary=summary,
        recommendations=recommendations,
        errors=errors
    )

    logger.info(f"Enrichment complete. Risk: {risk.level} ({risk.score:.2f})", extra={"correlation_id": correlation_id})
    return alert

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
