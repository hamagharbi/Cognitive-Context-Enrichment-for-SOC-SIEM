import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any

# Where you unzipped the Sigma rules
SIGMA_ROOT = Path(__file__).resolve().parent.parent / "sigma_rules"
OUT_DIR = Path(__file__).resolve().parent.parent / "rules" / "generated"

# Map ATT&CK tactics -> your intent labels
TACTIC_TO_INTENT = {
    "credential_access": "credential_harvesting",
    "execution": "execution",
    "persistence": "persistence_installation",
    "privilege_escalation": "privilege_escalation_attempt",
    "lateral_movement": "lateral_movement",
    "defense_evasion": "defense_evasion",
    "discovery": "reconnaissance",
    "collection": "data_staging",
    "exfiltration": "data_exfiltration",
    "command_and_control": "command_and_control_setup",
    "impact": "impact_operations",
}

def extract_tactic_and_technique(tags: List[str]):
    tactic = None
    technique_id = None

    for t in tags or []:
        if not isinstance(t, str):
            continue
        if t.startswith("attack.t"):
            # e.g. attack.t1562.006
            technique_id = t.split("attack.")[1]
        elif t.startswith("attack.") and not t.startswith("attack.t"):
            # e.g. attack.defense-evasion
            tactic = t.split("attack.")[1]

    return tactic, technique_id

def tactic_to_intent(tactic: str) -> str:
    if not tactic:
        return "unknown"
    tactic_key = tactic.lower().replace("-", "_")
    return TACTIC_TO_INTENT.get(tactic_key, "unknown")

def make_safe_id(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")

def build_rule_from_sigma(sigma_rule: Dict[str, Any]) -> Dict[str, Any] | None:
    tags = sigma_rule.get("tags", []) or []
    title = sigma_rule.get("title", "Sigma rule")
    description = sigma_rule.get("description", title)

    tactic, technique_id = extract_tactic_and_technique(tags)
    intent = tactic_to_intent(tactic)

    # If we got no useful mapping, skip (you can relax this if you like)
    if intent == "unknown" and not technique_id:
        return None

    # Regex seeds from title keywords
    keywords = [w for w in re.split(r"\W+", title) if len(w) > 3]
    if not keywords:
        keywords = [title]

    regexes = [re.escape(k.lower()) for k in keywords[:5]]

    rule_id_source = sigma_rule.get("id", title)
    rule_id = make_safe_id(f"sigma_{rule_id_source}")

    return {
        "id": rule_id,
        "intent": intent,
        "tactic": tactic.lower().replace("-", "_") if tactic else "unknown",
        "description": description,
        "conditions": {
            "summary": {
                "regex_any": regexes
            }
        },
        "weights": {
            "base": 0.6,
            "indicators_bonus": 0.1,
            "summary_bonus": 0.1,
        },
    }

def collect_sigma_files() -> List[Path]:
    if not SIGMA_ROOT.exists():
        raise SystemExit(f"Sigma rules folder not found at: {SIGMA_ROOT}")

    yml_files = []
    for p in SIGMA_ROOT.rglob("*.yml"):
        yml_files.append(p)
    return yml_files

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / "sigma_imported.yml"

    all_rules = []

    for yml in collect_sigma_files():
        try:
            with open(yml, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            continue

        if isinstance(data, list):
            items = data
        else:
            items = [data]

        for item in items:
            if not isinstance(item, dict):
                continue
            if "detection" not in item:
                continue
            rule = build_rule_from_sigma(item)
            if rule:
                all_rules.append(rule)

    if not all_rules:
        raise SystemExit("No rules generated from Sigma.")

    with open(out_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(all_rules, f, sort_keys=False, allow_unicode=True)

    print(f"Wrote {len(all_rules)} intent rules to {out_file}")

if __name__ == "__main__":
    main()
