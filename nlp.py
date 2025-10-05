# nlp.py
import re

def predict_intent(text: str) -> str:
    """
    Simple keyword-based intent detection for the Argo chatbot.
    Expanded to better catch:
    - comparisons (with or without explicit float numbers)
    - info/knowledge requests about temperature, salinity, pressure, Argo
    - synonyms like "temp", "sal", "psal", "pres", and trajectory variants
    """
    text_lower = text.lower()

    # Help / capabilities
    if (
        "help" in text_lower
        or "what can you do" in text_lower
        or "how to use" in text_lower
        or "commands" in text_lower
        or "options" in text_lower
    ):
        return "help"

    # List loaded floats
    if (
        "which floats" in text_lower
        or "loaded floats" in text_lower
        or "list floats" in text_lower
        or "show floats" in text_lower
        or "what floats" in text_lower
    ):
        return "list_floats"

    # Highest-priority: explicit float info
    if (
        ("float" in text_lower and "info" in text_lower)
        or ("details" in text_lower and "float" in text_lower)
        or ("about" in text_lower and "float" in text_lower)
        or ("summary" in text_lower and "float" in text_lower)
        or ("status" in text_lower and "float" in text_lower)
    ):
        return "float_info"

    # Comparisons (allow without explicit numbers; numbers are handled downstream)
    if (
        "compare" in text_lower
        or " vs " in text_lower
        or " versus " in text_lower
        or "difference between" in text_lower
    ):
        return "compare_floats"

    # Knowledge/info requests (e.g., "info regarding temp", "what is salinity")
    if (
        "info" in text_lower
        or "what is" in text_lower
        or "tell me about" in text_lower
        or "why" in text_lower
    ):
        if ("temperature" in text_lower) or re.search(r"\btemp\b", text_lower):
            return "importance_temperature"
        if ("salinity" in text_lower) or re.search(r"\bsal\b", text_lower) or ("psal" in text_lower):
            return "importance_salinity"
        if ("pressure" in text_lower) or ("pres" in text_lower):
            return "importance_pressure"
        if "argo" in text_lower:
            return "importance_argo"

    # Variable/profile queries
    if any(k in text_lower for k in [
        "temperature profile", "temp profile", "temp data", "temperature", "temp", "heat"
    ]):
        return "temperature"
    if any(k in text_lower for k in ["salinity", "psal", " sal "]):
        return "salinity"
    if any(k in text_lower for k in ["pressure", "pres", "depth profile", "depth data"]):
        return "pressure"

    # Trajectory
    if any(k in text_lower for k in [
        "trajectory", "path", "track", "route", "map", "position", "location", "where is"
    ]):
        return "trajectory"

    # Add float
    if (
        "add float" in text_lower
        or "load float" in text_lower
        or "include float" in text_lower
        or "add another float" in text_lower
    ):
        return "ask_float"

    # Greetings / Thanks
    if any(k in text_lower for k in ["hello", "hi", "hey", "good morning", "good evening"]):
        return "greeting"
    if any(k in text_lower for k in ["thanks", "thank you"]):
        return "thanks"
    if any(k in text_lower for k in ["bye", "goodbye", "see you"]):
        return "goodbye"

    # Specific knowledge phrasing
    if "importance of temperature" in text_lower:
        return "importance_temperature"
    if "importance of salinity" in text_lower:
        return "importance_salinity"
    if "importance of pressure" in text_lower:
        return "importance_pressure"
    if "why argo" in text_lower or "importance of argo" in text_lower or "why argo data" in text_lower:
        return "importance_argo"

    return "unknown"
