from ..schemas import NormalizedEvent
from ..utils import parse_timestamp
from typing import Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET
import re

def parse_xml_log(raw_log: str) -> Dict[str, Any]:
    extracted = {}
    try:
        clean_log = raw_log.strip()
        # Basic check for XML
        if not clean_log.startswith('<'):
            return {}
            
        root = ET.fromstring(clean_log)
        
        # Iterate all elements to flatten structure
        for elem in root.iter():
            # Remove namespace from tag
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag == 'EventID':
                extracted['EventID'] = elem.text
            elif tag == 'TimeCreated':
                extracted['TimeCreated'] = elem.get('SystemTime')
            elif tag == 'Computer':
                extracted['Computer'] = elem.text
            elif tag == 'Data':
                name = elem.get('Name')
                if name:
                    extracted[name] = elem.text
            elif tag == 'Security':
                userid = elem.get('UserID')
                if userid:
                    extracted['UserID'] = userid
                
    except Exception:
        pass
    return extracted

def parse_key_value(raw_log: str) -> Dict[str, Any]:
    extracted = {}
    
    # 1. Try to extract specific fields first (more reliable)
    # Event ID
    eid_match = re.search(r'Event\s*I?D\s*[:=]?\s*(\d+)', raw_log, re.IGNORECASE)
    if eid_match:
        extracted['EventID'] = eid_match.group(1)
        
    # User
    user_match = re.search(r'(?:User|Account Name|TargetUserName)\s*[:=]\s*([^\s,]+)', raw_log, re.IGNORECASE)
    if user_match:
        extracted['TargetUserName'] = user_match.group(1)

    # Computer
    comp_match = re.search(r'(?:Computer|Workstation Name)\s*[:=]\s*([^\s,]+)', raw_log, re.IGNORECASE)
    if comp_match:
        extracted['Computer'] = comp_match.group(1)

    # 2. Generic KV parsing, but stricter
    # Key must start with a letter, be at least 2 chars long.
    # Avoids matching timestamps like 15:30 as Key=15, Val=30
    matches = re.findall(r'(?:^|\s)([a-zA-Z][a-zA-Z0-9_\-\.\s]{1,})\s*[:=]\s*"?([^"\r\n]+)"?', raw_log)
    for k, v in matches:
        key = k.strip()
        val = v.strip()
        # Filter out common false positives
        if key.lower() in ['http', 'https', 'c', 'd', 'e', 'f']: 
            continue
        extracted[key] = val
        
    return extracted

def normalize(raw_log: str, fields: Dict[str, Any]) -> NormalizedEvent:
    # If fields are empty, try to parse the raw log
    if not fields:
        if raw_log.strip().startswith('<'):
            fields = parse_xml_log(raw_log)
        else:
            fields = parse_key_value(raw_log)

    # Assume fields might contain EventID, TimeCreated, etc.
    event_id = str(fields.get("EventID", fields.get("EventCode", "unknown")))
    
    # Map common EventIDs to event types
    event_type_map = {
        "4624": "logon_success",
        "4625": "logon_failed",
        "4688": "process_creation",
        "4720": "user_created",
        "4726": "user_deleted"
    }
    event_type = event_type_map.get(event_id, "windows_event")

    # Extract timestamp
    ts_str = fields.get("TimeCreated", fields.get("TimeGenerated", ""))
    timestamp = parse_timestamp(ts_str) if ts_str else datetime.utcnow()

    # Extract user/host
    user = fields.get("TargetUserName", fields.get("AccountName", None))
    hostname = fields.get("Computer", fields.get("ComputerName", None))

    message = f"Windows Event {event_id}: {event_type}"

    return NormalizedEvent(
        timestamp=timestamp,
        source="windows_eventlog",
        event_type=event_type,
        hostname=hostname,
        user=user,
        message=message,
        raw_log=raw_log,
        normalized_fields=fields
    )
