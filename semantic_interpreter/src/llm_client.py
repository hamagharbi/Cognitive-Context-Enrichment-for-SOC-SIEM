import os
import json
import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv

from .prompts import SYSTEM_PROMPT, LOG_ANALYSIS_TEMPLATE
from .parser import LogAnalysis

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def get_semantic_interpretation(log_json: dict):
    raw_log = log_json.get("raw_log", "")
    known_fields = log_json.get("known_fields", {})

    user_prompt = LOG_ANALYSIS_TEMPLATE.format(
        log_entry=raw_log,
        known_fields=json.dumps(known_fields)
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    for attempt in range(3):
        try:
            completion = await client.chat.completions.create(
                model="qwen/qwen3-32b",
                temperature=0,
                response_format={"type": "json_object"},
                messages=messages
            )

            content = completion.choices[0].message.content
            parsed = json.loads(content)
            validated = LogAnalysis(**parsed)
            return validated.model_dump()

        except Exception as e:
            print(f"JSON parse error (attempt {attempt+1}):", str(e))
            await asyncio.sleep(1)

    raise RuntimeError("Failed to generate valid JSON after 3 attempts.")
