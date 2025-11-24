from ..schemas import NormalizedEvent
from ..utils import extract_key_value, parse_timestamp
from typing import Dict, Any
from datetime import datetime

def normalize(raw_log: str, fields: Dict[str, Any]) -> NormalizedEvent:
    # If fields are empty, try to parse raw_log
    if not fields:
        fields = extract_key_value(raw_log)

    # Auditd specific
    # type=EXECVE msg=audit(162...): ...
    
    audit_type = fields.get("type", "UNKNOWN")
    
    # Map type to event_type
    if audit_type == "EXECVE":
        event_type = "process_execution"
    elif audit_type == "SYSCALL":
        event_type = "system_call"
    elif audit_type == "AVC":
        event_type = "access_control"
    else:
        event_type = "audit_event"

    # Timestamp is usually inside msg=audit(TIMESTAMP:ID)
    # We can try to extract it, or just use current time if complex
    # Example: msg=audit(1621234567.123:123)
    timestamp = datetime.utcnow()
    msg = fields.get("msg", "")
    if "audit(" in msg:
        try:
            # Extract epoch
            import re
            match = re.search(r'audit\((\d+\.\d+):', msg)
            if match:
                epoch = float(match.group(1))
                timestamp = datetime.fromtimestamp(epoch)
        except:
            pass

    # User/Host
    # uid=0 or auid=1000 -> need to map to username if possible, but here we just store ID
    user = fields.get("uid", fields.get("auid", None))
    hostname = None # Auditd logs often don't have hostname inside the line itself

    message = f"Auditd {audit_type}"
    if "exe" in fields:
        message += f" exe={fields['exe']}"

    return NormalizedEvent(
        timestamp=timestamp,
        source="linux_auditd",
        event_type=event_type,
        hostname=hostname,
        user=user,
        message=message,
        raw_log=raw_log,
        normalized_fields=fields
    )
