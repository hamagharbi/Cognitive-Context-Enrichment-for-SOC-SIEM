import logging
import sys
from .config import settings

# Create logger
logger = logging.getLogger("enrichment_orchestrator")
logger.setLevel(settings.ORCHESTRATOR_LOG_LEVEL)

# Create console handler
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(settings.ORCHESTRATOR_LOG_LEVEL)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [CorrelationID: %(correlation_id)s] - %(message)s'
)
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)

# Filter to inject default correlation_id if missing
class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = 'N/A'
        return True

logger.addFilter(CorrelationIdFilter())
