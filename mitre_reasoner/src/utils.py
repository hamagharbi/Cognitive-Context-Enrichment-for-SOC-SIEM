import re
from typing import Optional

def extract_technique_id(url: Optional[str]) -> Optional[str]:
    """
    Extracts T-code from MITRE URL.
    Example: https://attack.mitre.org/techniques/T1001 -> T1001
    """
    if not url:
        return None
    match = re.search(r'(T\d+(\.\d+)?)', url)
    return match.group(1) if match else None
