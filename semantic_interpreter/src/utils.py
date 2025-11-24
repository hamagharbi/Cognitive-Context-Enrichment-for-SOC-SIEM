def preprocess_log(log_text: str) -> str:
    """
    Cleans and normalizes a log string.
    No LangChain needed.
    """
    if not log_text:
        return ""
    return " ".join(log_text.split())
