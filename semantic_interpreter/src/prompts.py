SYSTEM_PROMPT = """
You are a cybersecurity log interpretation engine.
You MUST output ONLY valid JSON.
No explanations. No markdown. No code fences.
Return strictly the JSON object requested.
"""

LOG_ANALYSIS_TEMPLATE = """
Analyze the following security log and extract a semantic interpretation.

RAW_LOG:
{log_entry}

KNOWN_FIELDS:
{known_fields}

Return ONLY valid JSON with EXACTLY this structure:

{{
  "semantic_summary": "<one-sentence summary>",
  "semantic_features": {{
      "operation_type": "<string>",
      "resource_type": "<string>",
      "access_channel": "<string>",
      "direction": "<string>",
      "suspicious_indicators": []
  }},
  "confidence": 0.0
}}
"""
