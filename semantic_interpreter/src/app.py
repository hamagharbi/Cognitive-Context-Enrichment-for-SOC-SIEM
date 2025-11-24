import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from .llm_client import get_semantic_interpretation
from .parser import LogAnalysis
from .utils import preprocess_log

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("semantic_interpreter")

app = FastAPI(title="Semantic Log Interpreter")

class LogInput(BaseModel):
    raw_log: str = Field(..., description="The raw log text to interpret")
    fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context fields extracted from the log")

@app.post("/interpret", response_model=LogAnalysis)
async def interpret_log(input_data: LogInput):
    """
    Endpoint to interpret a raw log line and return a structured semantic analysis.
    """
    logger.info(f"Received interpretation request. Log preview: {input_data.raw_log[:50]}...")
    
    try:
        # 1. Preprocess
        clean_log = preprocess_log(input_data.raw_log)
        
        if not clean_log:
            logger.warning("Log text is empty after preprocessing.")
            raise HTTPException(status_code=400, detail="Log text is empty")

        # 2. Prepare Input for LLM
        # Combine raw log and any pre-extracted fields into a single context for the LLM
        llm_input = {
            "raw_log": clean_log,
            "known_fields": input_data.fields
        }

        # 3. Call LLM Client
        logger.info("Dispatching to Groq LLM...")
        result = await get_semantic_interpretation(llm_input)
        
        logger.info("Successfully received interpretation from LLM.")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal error during interpretation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
