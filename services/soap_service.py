def generate_soap(text):
    text = text.lower()

    symptoms = []
    if "fever" in text: symptoms.append("Fever")
    if "cough" in text: symptoms.append("Cough")
    if "pain" in text: symptoms.append("Pain")
    if "fatigue" in text: symptoms.append("Fatigue")

    # Build SOAP
    soap = f"""
S — Subjective:
Patient reports: {text}

O — Objective:
No clinical measurements available (voice-based input).

A — Assessment:
Possible conditions based on symptoms: {", ".join(symptoms) if symptoms else "General illness"}

P — Plan:
- Recommend rest and hydration
- Monitor symptoms
- Seek medical consultation if condition worsens
"""

    return soap.strip()