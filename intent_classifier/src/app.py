from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List, Optional

from .models import SemanticInput, IntentClassificationResult, Rule
from .rule_loader import load_rules
from .engine import evaluate_rules
from .llm_fallback import llm_pick_intent
from .utils import logger, INTENT_RULE_CONFIDENCE_THRESHOLD, INTENT_LLM_FALLBACK_ENABLED

# Global state for rules
rules: List[Rule] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global rules
    logger.info("Loading rules...")
    rules = load_rules("rules") # Assumes rules/ is in the CWD or relative to it
    logger.info(f"Startup complete. {len(rules)} rules active.")
    yield
    # Shutdown
    rules.clear()

app = FastAPI(title="Intent Classifier", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok", "rules_loaded": len(rules)}

@app.post("/classify_intent", response_model=IntentClassificationResult)
async def classify_intent(input_data: SemanticInput, debug: bool = False):
    """
    Classifies the intent of a log based on semantic analysis.
    Uses rule-based engine first, falls back to LLM if confidence is low.
    """
    logger.info(f"Received classification request for: {input_data.semantic_summary[:50]}...")
    
    # 1. Evaluate Rules
    engine_result = evaluate_rules(input_data, rules)
    
    best_intent = engine_result["best_intent"]
    best_score = engine_result["best_score"]
    best_tactic = engine_result["best_tactic"]
    matched_rules = engine_result["matched_rules"]
    candidates = engine_result["candidates"]

    # 2. Check Threshold
    if best_score >= INTENT_RULE_CONFIDENCE_THRESHOLD:
        logger.info(f"Rule matched with high confidence: {best_intent} ({best_score})")
        return IntentClassificationResult(
            intent=best_intent,
            tactic=best_tactic,
            score=best_score,
            matched_rules=matched_rules,
            source="rules",
            explanation="High confidence rule match",
            debug_info=engine_result if debug else None
        )
    
    # 3. Fallback
    if INTENT_LLM_FALLBACK_ENABLED:
        logger.info(f"Low rule confidence ({best_score}). Falling back to LLM.")
        llm_result = await llm_pick_intent(input_data, candidates)
        
        if debug:
            llm_result.debug_info = engine_result
            
        return llm_result
    
    # 4. Return best rule result anyway if fallback disabled
    logger.info(f"Low rule confidence ({best_score}) and fallback disabled. Returning best rule match.")
    return IntentClassificationResult(
        intent=best_intent if best_intent else "unknown",
        tactic=best_tactic,
        score=best_score,
        matched_rules=matched_rules,
        source="rules",
        explanation="Low confidence rule match (fallback disabled)",
        debug_info=engine_result if debug else None
    )
