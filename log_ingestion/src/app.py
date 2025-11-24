from fastapi import FastAPI, HTTPException
from .schemas import IngestRequest, NormalizedEvent
from .detectors.log_type_detector import detect_log_type
from .normalizers import (
    windows_eventlog,
    sysmon,
    linux_auditd,
    generic_syslog
)

app = FastAPI(title="Log Ingestion & Normalization")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/ingest", response_model=NormalizedEvent)
async def ingest_log(request: IngestRequest):
    """
    Ingests a raw log, detects its type, and normalizes it.
    """
    # 1. Detect Type
    log_type = detect_log_type(request.raw_log, request.fields, request.source_type)
    
    # 2. Dispatch to Normalizer
    try:
        if log_type == "windows_eventlog":
            normalized = windows_eventlog.normalize(request.raw_log, request.fields)
        elif log_type == "sysmon":
            normalized = sysmon.normalize(request.raw_log, request.fields)
        elif log_type == "linux_auditd":
            normalized = linux_auditd.normalize(request.raw_log, request.fields)
        else:
            # Fallback
            normalized = generic_syslog.normalize(request.raw_log, request.fields)
            
    except Exception as e:
        # In production, log this error
        raise HTTPException(status_code=500, detail=f"Normalization failed: {str(e)}")

    return normalized

