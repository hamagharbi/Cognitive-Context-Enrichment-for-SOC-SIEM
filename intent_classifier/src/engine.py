import re
from typing import List, Dict, Any
from .models import SemanticInput, Rule
from .utils import logger

def evaluate_rules(semantic: SemanticInput, rules: List[Rule]) -> Dict[str, Any]:
    """
    Evaluates all rules against the semantic input.
    Returns the best intent, tactic, score, and matched rules.
    """
    intent_scores: Dict[str, Dict[str, Any]] = {}

    for rule in rules:
        score = _evaluate_single_rule(semantic, rule)
        
        if score > 0:
            if rule.intent not in intent_scores:
                intent_scores[rule.intent] = {
                    "scores": [],
                    "tactics": [],
                    "matched_rules": []
                }
            intent_scores[rule.intent]["scores"].append(score)
            intent_scores[rule.intent]["tactics"].append(rule.tactic)
            intent_scores[rule.intent]["matched_rules"].append(rule.id)

    # Find the best intent
    best_intent = None
    best_score = 0.0
    best_tactic = "unknown"
    best_matched_rules = []
    
    candidates = {}

    for intent, data in intent_scores.items():
        max_score = max(data["scores"])
        
        # Determine tactic (simple majority or take from max score)
        # Here we take the tactic associated with the highest score for this intent
        # If multiple rules have same max score, we take the first one's tactic
        max_idx = data["scores"].index(max_score)
        tactic = data["tactics"][max_idx]
        
        candidates[intent] = {
            "score": max_score,
            "tactic": tactic,
            "matched_rules": data["matched_rules"]
        }

        if max_score > best_score:
            best_score = max_score
            best_intent = intent
            best_tactic = tactic
            best_matched_rules = data["matched_rules"]

    return {
        "best_intent": best_intent,
        "best_tactic": best_tactic,
        "best_score": best_score,
        "matched_rules": best_matched_rules,
        "candidates": candidates
    }

def _evaluate_single_rule(semantic: SemanticInput, rule: Rule) -> float:
    conditions = rule.conditions
    weights = rule.weights
    
    matched_conditions = 0
    total_conditions_checked = 0
    
    # 1. Summary Regex
    if "summary" in conditions and "regex_any" in conditions["summary"]:
        total_conditions_checked += 1
        regexes = conditions["summary"]["regex_any"]
        if _check_regex_any(semantic.semantic_summary, regexes):
            matched_conditions += 1
        else:
            return 0.0 # Strict fail if specified condition not met? 
            # Actually, usually rules are AND logic for top-level keys. 
            # If a condition block exists, it must be satisfied.

    # 2. Suspicious Indicators
    if "suspicious_indicators" in conditions:
        indicators = semantic.semantic_features.get("suspicious_indicators", [])
        
        if "contains_any" in conditions["suspicious_indicators"]:
            total_conditions_checked += 1
            required = conditions["suspicious_indicators"]["contains_any"]
            if not _check_contains_any(indicators, required):
                return 0.0
            matched_conditions += 1
            
        if "contains_all" in conditions["suspicious_indicators"]:
            total_conditions_checked += 1
            required = conditions["suspicious_indicators"]["contains_all"]
            if not _check_contains_all(indicators, required):
                return 0.0
            matched_conditions += 1

    # 3. Operation Type
    if "operation_type" in conditions:
        op_type = semantic.semantic_features.get("operation_type", "")
        if "any_of" in conditions["operation_type"]:
            total_conditions_checked += 1
            allowed = conditions["operation_type"]["any_of"]
            if op_type not in allowed:
                return 0.0
            matched_conditions += 1

    # 4. Resource Type
    if "resource_type" in conditions:
        res_type = semantic.semantic_features.get("resource_type", "")
        if "contains_any" in conditions["resource_type"]:
            total_conditions_checked += 1
            substrings = conditions["resource_type"]["contains_any"]
            if not any(sub in res_type for sub in substrings):
                return 0.0
            matched_conditions += 1

    # If we got here, all checked conditions passed
    # Calculate score
    score = weights.get("base", 0.0)
    
    # Apply bonuses
    # Indicators bonus: if any suspicious indicators are present (and we didn't already fail a check)
    if weights.get("indicators_bonus", 0.0) > 0:
        if semantic.semantic_features.get("suspicious_indicators"):
            score += weights["indicators_bonus"]
            
    # Summary bonus: if regex matched (we already checked this above, but bonus applies if condition existed)
    if weights.get("summary_bonus", 0.0) > 0:
        if "summary" in conditions and "regex_any" in conditions["summary"]:
             score += weights["summary_bonus"]

    return max(0.0, min(score, 1.0))

def _check_regex_any(text: str, patterns: List[str]) -> bool:
    for pattern in patterns:
        try:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        except re.error:
            logger.warning(f"Invalid regex pattern: {pattern}")
    return False

def _check_contains_any(actual: List[str], required: List[str]) -> bool:
    actual_set = {s.lower() for s in actual}
    for req in required:
        if req.lower() in actual_set:
            return True
    return False

def _check_contains_all(actual: List[str], required: List[str]) -> bool:
    actual_set = {s.lower() for s in actual}
    for req in required:
        if req.lower() not in actual_set:
            return False
    return True
