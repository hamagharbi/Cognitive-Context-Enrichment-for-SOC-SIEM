import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
# src/utils.py -> intent_classifier/ -> CCE/ (root)
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

# Fallback: try loading from current directory just in case
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
INTENT_RULE_CONFIDENCE_THRESHOLD = float(os.getenv("INTENT_RULE_CONFIDENCE_THRESHOLD", "0.7"))
INTENT_LLM_FALLBACK_ENABLED = os.getenv("INTENT_LLM_FALLBACK_ENABLED", "true").lower() == "true"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("intent_classifier")
