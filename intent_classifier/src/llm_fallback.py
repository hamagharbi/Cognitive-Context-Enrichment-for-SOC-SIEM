import os
import json
import asyncio
from typing import Dict, Any
from groq import AsyncGroq
from .models import SemanticInput, IntentClassificationResult
from .utils import GROQ_API_KEY, logger

client = AsyncGroq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a cybersecurity SOC assistant that classifies high-level attack intent from semantic log analysis. 
Answer ONLY with a JSON object.
"""

async def llm_pick_intent(semantic: SemanticInput, candidates: Dict[str, Any]) -> IntentClassificationResult:
    """
    Uses LLM to pick the best intent when rule-based confidence is low.
    """
    
    # Construct a summary of candidates for the LLM
    candidates_summary = []
    for intent, data in candidates.items():
        candidates_summary.append({
            "intent": intent,
            "tactic": data["tactic"],
            "rule_score": data["score"]
        })

    user_content = {
        "semantic_summary": semantic.semantic_summary,
        "semantic_features": semantic.semantic_features,
        "rule_based_candidates": candidates_summary,
        "instruction": "Analyze the semantic summary and features. Choose the most likely MITRE ATT&CK intent and tactic. If the rule-based candidates are good, select the best one. If they are wrong, propose a better one. Provide a confidence score (0.0-1.0)."
    }

    user_prompt = json.dumps(user_content, indent=2)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    logger.info("Dispatching to Groq LLM for intent fallback...")

    for attempt in range(3):
        try:
            completion = await client.chat.completions.create(
                model="qwen/qwen3-32b", # Using the model requested/used in other services
                temperature=0,
                response_format={"type": "json_object"},
                messages=messages
            )

            content = completion.choices[0].message.content
            parsed = json.loads(content)
            
            # Expected JSON structure:
            # {
            #   "intent": "...",
            #   "tactic": "...",
            #   "score": 0.8,
            #   "explanation": "..."
            # }
            
            return IntentClassificationResult(
                intent=parsed.get("intent", "unknown"),
                tactic=parsed.get("tactic", "unknown"),
                score=float(parsed.get("score", 0.5)),
                matched_rules=[],
                source="llm",
                explanation=parsed.get("explanation", "LLM generated")
            )

        except Exception as e:
            logger.error(f"LLM fallback error (attempt {attempt+1}): {e}")
            await asyncio.sleep(1)

    # Fallback if LLM fails completely
    return IntentClassificationResult(
        intent="unknown",
        tactic="unknown",
        score=0.0,
        matched_rules=[],
        source="llm",
        explanation="LLM fallback failed"
    )
