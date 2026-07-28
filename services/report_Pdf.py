import re
import pdfplumber

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace(",", "")
    return text


def extract_values(text):
    patterns = {
        "hemoglobin": r'(hemoglobin|hgb|haemoglobin)\s*[:\-]?\s*([\d.]+)',
        "wbc": r'(wbc|white blood cells?)\s*[:\-]?\s*([\d.]+)',
        "platelets": r'(platelet[s]?)\s*[:\-]?\s*([\d.]+)',
        "glucose": r'(glucose|blood sugar)\s*[:\-]?\s*([\d.]+)',
        "hba1c": r'(hba1c)\s*[:\-]?\s*([\d.]+)',
        "cholesterol": r'(total cholesterol)\s*[:\-]?\s*([\d.]+)',
        "ldl": r'(ldl)\s*[:\-]?\s*([\d.]+)',
        "hdl": r'(hdl)\s*[:\-]?\s*([\d.]+)',
        "triglycerides": r'(triglycerides?)\s*[:\-]?\s*([\d.]+)',
        "alt": r'(alt|sgpt)\s*[:\-]?\s*([\d.]+)',
        "ast": r'(ast|sgot)\s*[:\-]?\s*([\d.]+)',
        "creatinine": r'(creatinine)\s*[:\-]?\s*([\d.]+)'
    }

    data = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            try:
                data[key] = float(match.group(2))
            except:
                pass

    return data


def analyze_values(data):
    findings = []

    if "hemoglobin" in data:
        if data["hemoglobin"] < 13:
            findings.append(f" Low haemoglobin ({data['hemoglobin']}) → anaemia.")
        else:
            findings.append(f" Normal haemoglobin ({data['hemoglobin']}).")

    if "glucose" in data:
        if data["glucose"] > 126:
            findings.append(f" High glucose ({data['glucose']}) → diabetes risk.")

    if "hba1c" in data:
        if data["hba1c"] > 6.5:
            findings.append(f" HbA1c high ({data['hba1c']}) → diabetes.")

    if "cholesterol" in data and data["cholesterol"] > 200:
        findings.append(f" High cholesterol ({data['cholesterol']}).")

    if "ldl" in data and data["ldl"] > 130:
        findings.append(f" High LDL ({data['ldl']}).")

    if "hdl" in data and data["hdl"] < 40:
        findings.append(f" Low HDL ({data['hdl']}).")

    if "triglycerides" in data and data["triglycerides"] > 150:
        findings.append(f" High triglycerides ({data['triglycerides']}).")

    if "creatinine" in data and data["creatinine"] > 1.3:
        findings.append(f" High creatinine ({data['creatinine']}) → kidney issue.")

    if not findings:
        findings.append("ℹ No major abnormal values detected.")

    return findings


def generate_recommendations(data):
    advice = []

    if "hemoglobin" in data and data["hemoglobin"] < 13:
        advice.append(" Increase iron intake.")

    if "glucose" in data and data["glucose"] > 126:
        advice.append(" Reduce sugar intake.")

    if "cholesterol" in data and data["cholesterol"] > 200:
        advice.append(" Low-fat diet + exercise.")

    if "creatinine" in data:
        advice.append(" Stay hydrated, monitor kidney health.")

    return advice


def process_report(text):
    text = clean_text(text)
    extracted = extract_values(text)

    findings = analyze_values(extracted)
    advice = generate_recommendations(extracted)

    return {
        "extracted": extracted,
        "findings": findings,
        "advice": advice
    }