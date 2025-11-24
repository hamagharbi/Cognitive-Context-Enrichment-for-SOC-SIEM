from ..schemas import NormalizedEvent
from typing import Dict, Any
from datetime import datetime
import re
import dateutil.parser

def parse_syslog(raw_log: str) -> Dict[str, Any]:
    extracted = {}
    # RFC3164: <PRI>Mmm dd hh:mm:ss HOSTNAME TAG: CONTENT
    # Example: Nov 23 15:30:00 myhost myapp[123]: message content
    
    # Regex for BSD style (Mmm dd hh:mm:ss)
    bsd_regex = r'^([A-Z][a-z]{2}\s+\d+\s\d{2}:\d{2}:\d{2})\s+([^\s]+)\s+([^:\[]+)(?:\[(\d+)\])?:\s+(.*)$'
    match = re.search(bsd_regex, raw_log)
    if match:
        extracted['timestamp'] = match.group(1)
        extracted['hostname'] = match.group(2)
        extracted['app_name'] = match.group(3)
        if match.group(4):
            extracted['pid'] = match.group(4)
        extracted['message'] = match.group(5)
        return extracted

    # RFC5424: <PRI>VER TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCT-DATA MSG
    # Simplified: TIMESTAMP HOSTNAME APP ...
    iso_regex = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2}))\s+([^\s]+)\s+([^\s]+)\s+(.*)$'
    match = re.search(iso_regex, raw_log)
    if match:
        extracted['timestamp'] = match.group(1)
        extracted['hostname'] = match.group(2)
        extracted['app_name'] = match.group(3)
        extracted['message'] = match.group(4)
        return extracted

    return {}

def normalize(raw_log: str, fields: Dict[str, Any]) -> NormalizedEvent:
    # Generic fallback
    # Try to find common syslog fields if parsed
    
    if not fields:
        fields = parse_syslog(raw_log)

    timestamp = datetime.utcnow()
    # If fields has 'timestamp' or 'date'
    if "timestamp" in fields:
        try:
            timestamp = dateutil.parser.parse(fields["timestamp"])
        except:
            pass
    
    hostname = fields.get("host", fields.get("hostname", None))
    app_name = fields.get("app_name", fields.get("program", "syslog"))
    
    message = fields.get("message", raw_log)
    
    return NormalizedEvent(
        timestamp=timestamp,
        source="generic_syslog",
        event_type="log_message",
        hostname=hostname,
        user=None,
        message=f"{app_name}: {message[:50]}...",
        raw_log=raw_log,
        normalized_fields=fields
    )
