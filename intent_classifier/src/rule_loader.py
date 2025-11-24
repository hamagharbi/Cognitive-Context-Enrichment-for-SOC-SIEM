import os
import yaml
from typing import List
from .models import Rule
from .utils import logger

def load_rules(rules_dir: str = "rules") -> List[Rule]:
    loaded_rules = []
    
    # Walk through the rules directory
    for root, _, files in os.walk(rules_dir):
        for file in files:
            if file.endswith(".yml") or file.endswith(".yaml"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        
                        # Handle list of rules in a single file
                        if isinstance(data, list):
                            for item in data:
                                try:
                                    rule = _parse_rule(item)
                                    loaded_rules.append(rule)
                                except Exception as e:
                                    logger.error(f"Error parsing rule in {file}: {e}")
                        elif isinstance(data, dict):
                            try:
                                rule = _parse_rule(data)
                                loaded_rules.append(rule)
                            except Exception as e:
                                logger.error(f"Error parsing rule in {file}: {e}")
                                
                except Exception as e:
                    logger.error(f"Failed to load file {file_path}: {e}")

    logger.info(f"Loaded {len(loaded_rules)} rules from {rules_dir}")
    return loaded_rules

def _parse_rule(data: dict) -> Rule:
    # Normalize tactic
    tactic = data.get("tactic", "unknown").lower().replace(" ", "_")
    
    # Ensure required fields are present (Pydantic will validate, but we can do pre-processing here)
    return Rule(
        id=data["id"],
        intent=data["intent"],
        tactic=tactic,
        description=data.get("description", ""),
        conditions=data.get("conditions", {}),
        weights=data.get("weights", {})
    )
