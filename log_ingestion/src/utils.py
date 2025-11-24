from datetime import datetime
import dateutil.parser

def parse_timestamp(ts_str: str) -> datetime:
    try:
        return dateutil.parser.parse(ts_str)
    except:
        return datetime.utcnow()

def extract_key_value(text: str) -> dict:
    """
    Extracts key=value pairs from a string.
    Handles quoted values roughly.
    """
    result = {}
    # Simple regex for key=value or key="value"
    import re
    pattern = re.compile(r'([a-zA-Z0-9_]+)=(?:"([^"]+)"|([^ ]+))')
    for match in pattern.finditer(text):
        key = match.group(1)
        val = match.group(2) if match.group(2) is not None else match.group(3)
        result[key] = val
    return result
