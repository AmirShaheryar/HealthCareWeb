def detect_risk(text):
    text = text.lower()

    critical_keywords = ["chest pain", "heart attack", "unable to breathe", "severe bleeding"]
    high_keywords = ["high fever", "vomiting", "infection"]
    medium_keywords = ["pain", "fatigue", "cough"]

    for word in critical_keywords:
        if word in text:
            return "🔴 Critical"

    for word in high_keywords:
        if word in text:
            return "🟠 High"

    for word in medium_keywords:
        if word in text:
            return "🟡 Medium"

    return "🟢 Low"