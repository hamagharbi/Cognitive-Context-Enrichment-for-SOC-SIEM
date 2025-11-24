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
        if not clean_log.startswith('<'):
            return {}
        root = ET.fromstring(clean_log)
        for elem in root.iter():
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
    except Exception:
        pass
    return extracted

def parse_key_value(raw_log: str) -> Dict[str, Any]:
    extracted = {}
    # 1. Try to extract specific fields first
    eid_match = re.search(r'Event\s*I?D\s*[:=]?\s*(\d+)', raw_log, re.IGNORECASE)
    if eid_match:
        extracted['EventID'] = eid_match.group(1)
        
    user_match = re.search(r'(?:User|Account Name|TargetUserName)\s*[:=]\s*([^\s,]+)', raw_log, re.IGNORECASE)
    if user_match:
        extracted['User'] = user_match.group(1)

    comp_match = re.search(r'(?:Computer|Workstation Name)\s*[:=]\s*([^\s,]+)', raw_log, re.IGNORECASE)
    if comp_match:
        extracted['Computer'] = comp_match.group(1)

    # 2. Generic KV parsing
    matches = re.findall(r'(?:^|\s)([a-zA-Z][a-zA-Z0-9_\-\.\s]{1,})\s*[:=]\s*"?([^"\r\n]+)"?', raw_log)
    for k, v in matches:
        key = k.strip()
        val = v.strip()
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

    # Sysmon Event IDs
    # 1: Process Create
    # 3: Network Connect
    # 11: File Create
    # 12/13/14: Registry
    
    event_id = str(fields.get("EventID", "unknown"))
    
    event_type_map = {
        "1": "process_creation",
        "3": "network_connection",
        "11": "file_creation",
        "12": "registry_event",
        "13": "registry_event",
        "22": "dns_query"
    }
    event_type = event_type_map.get(event_id, "sysmon_event")

    ts_str = fields.get("UtcTime", fields.get("TimeCreated", ""))
    timestamp = parse_timestamp(ts_str) if ts_str else datetime.utcnow()

    # Sysmon specific fields
    user = fields.get("User", None)
    hostname = fields.get("Computer", None)
    
    # Construct a message
    image = fields.get("Image", "")
    command_line = fields.get("CommandLine", "")
    
    if event_id == "1":
        message = f"Process Create: {image} ({command_line})"
    elif event_id == "3":
        dest_ip = fields.get("DestinationIp", "")
        dest_port = fields.get("DestinationPort", "")
        message = f"Network Connect: {image} -> {dest_ip}:{dest_port}"
    else:
        message = f"Sysmon Event {event_id}"

    return NormalizedEvent(
        timestamp=timestamp,
        source="sysmon",
        event_type=event_type,
        hostname=hostname,
        user=user,
        message=message,
        raw_log=raw_log,
        normalized_fields=fields
    )
