import re
from typing import Dict, Any

def detect_log_type(raw_log: str, fields: Dict[str, Any] = None, hint: str = None) -> str:
    """
    Detects the log type based on the raw log content, parsed fields, or an optional hint.
    """
    if hint:
        return hint.lower()

    raw_lower = raw_log.lower()
    fields = fields or {}

    # 1. Sysmon
    # Often contains "Microsoft-Windows-Sysmon" or EventID 1, 3, etc. with specific provider
    if "microsoft-windows-sysmon" in raw_lower:
        return "sysmon"
    if fields.get("ProviderName") == "Microsoft-Windows-Sysmon":
        return "sysmon"
    if "<Provider Name='Microsoft-Windows-Sysmon'" in raw_log:
        return "sysmon"

    # 2. Windows Security / EventLog
    # "Microsoft-Windows-Security-Auditing"
    if "microsoft-windows-security-auditing" in raw_lower:
        return "windows_eventlog"
    if "eventcode" in fields or "EventID" in fields:
        # Fallback for generic windows if not sysmon
        return "windows_eventlog"

    # 3. Linux Auditd
    # "type=SYSCALL", "type=EXECVE", "type=AVC"
    if "type=" in raw_log and "msg=audit" in raw_log:
        return "linux_auditd"
    
    # 4. Apache Access
    # Common pattern: IP - - [Date] "Request" Status Size
    if re.search(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s+-\s+-\s+\[', raw_log):
        return "apache_access"

    # 5. CloudTrail
    if "cloudtrail" in raw_lower or "eventsource" in raw_lower:
        return "cloudtrail"

    # Default
    return "generic_syslog"
