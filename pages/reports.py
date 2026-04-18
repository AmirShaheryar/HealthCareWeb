import streamlit as st
import re

SAMPLE_REPORTS = {
    "CBC Blood Report": """
COMPLETE BLOOD COUNT (CBC) REPORT
Patient: Ali Raza | DOB: 1985-03-12 | Lab ID: LAB-2024-1023
Date: 2024-11-15

Hemoglobin: 11.2 g/dL (Reference: 13.5–17.5 g/dL) [LOW] ↓
Hematocrit: 34% (Reference: 41–53%) [LOW] ↓
WBC Count: 10,800 /µL (Reference: 4,500–11,000 /µL) [NORMAL]
Platelet Count: 245,000 /µL (Reference: 150,000–400,000 /µL) [NORMAL]
MCV: 72 fL (Reference: 80–100 fL) [LOW] ↓
MCH: 24 pg (Reference: 27–33 pg) [LOW] ↓
RBC Count: 3.8 × 10^6/µL (Reference: 4.5–5.9 × 10^6/µL) [LOW] ↓
Serum Ferritin: 8 ng/mL (Reference: 12–300 ng/mL) [LOW] ↓

Impression: Microcytic hypochromic anaemia, consistent with Iron Deficiency Anaemia (IDA).
Recommend oral iron supplementation and dietary counselling. Repeat CBC in 8 weeks.
    """,
    "Lipid Profile Report": """
LIPID PROFILE TEST
Patient: Sara Khan | Age: 48 | Gender: Female
Date: 2024-10-20

Total Cholesterol: 242 mg/dL (Desirable: <200 mg/dL) [HIGH] ↑
LDL Cholesterol: 158 mg/dL (Optimal: <100 mg/dL) [HIGH] ↑
HDL Cholesterol: 38 mg/dL (Desirable: >60 mg/dL) [LOW] ↓
Triglycerides: 210 mg/dL (Normal: <150 mg/dL) [HIGH] ↑
VLDL: 42 mg/dL (Normal: 2–30 mg/dL) [HIGH] ↑
Total Cholesterol/HDL Ratio: 6.4 (Risk: >5) [ELEVATED RISK] ↑

Clinical Interpretation: Dyslipidaemia with elevated cardiovascular risk. Patient advised to 
initiate statin therapy (Atorvastatin 20mg), adopt a low-fat Mediterranean diet, and increase 
aerobic physical activity. Follow-up lipid panel in 3 months.
    """,
}

def simplify_report(raw_text):
    """NLP-based simplification of medical report text."""
    raw_lower = raw_text.lower()
    findings = []
    advice_items = []

    # Detect abnormal values
    if re.search(r'hemoglobin|hgb|haemoglobin', raw_lower):
        low_hgb = re.search(r'hemoglobin[^\d]*([\d.]+)', raw_lower)
        if low_hgb:
            val = float(low_hgb.group(1))
            if val < 13:
                findings.append(f"🔴 Your **haemoglobin** ({val} g/dL) is **below normal**. This means your blood may not be carrying enough oxygen — this is called anaemia.")
            else:
                findings.append(f"✅ Your **haemoglobin** ({val} g/dL) is within a healthy range.")

    if re.search(r'cholesterol', raw_lower):
        chol = re.search(r'total cholesterol[^\d]*([\d.]+)', raw_lower)
        if chol:
            val = float(chol.group(1))
            if val > 200:
                findings.append(f"🔴 Your **total cholesterol** ({val} mg/dL) is **too high**. High cholesterol can clog arteries and increase risk of heart disease.")
            else:
                findings.append(f"✅ Your **total cholesterol** ({val} mg/dL) looks good.")

        ldl = re.search(r'ldl[^\d]*([\d.]+)', raw_lower)
        if ldl:
            val = float(ldl.group(1))
            if val > 130:
                findings.append(f"🔴 Your **LDL (bad cholesterol)** ({val} mg/dL) is **elevated**. This is the type of cholesterol that builds up in blood vessels.")

        hdl = re.search(r'hdl[^\d]*([\d.]+)', raw_lower)
        if hdl:
            val = float(hdl.group(1))
            if val < 40:
                findings.append(f"🟡 Your **HDL (good cholesterol)** ({val} mg/dL) is **low**. You want this number higher — it helps remove bad cholesterol from your blood.")

    if re.search(r'triglyceride', raw_lower):
        trig = re.search(r'triglycerides[^\d]*([\d.]+)', raw_lower)
        if trig:
            val = float(trig.group(1))
            if val > 150:
                findings.append(f"🔴 Your **triglycerides** ({val} mg/dL) are **high**. This is a type of fat in the blood, often linked to high-sugar diet.")

    if re.search(r'ferritin', raw_lower):
        fer = re.search(r'ferritin[^\d]*([\d.]+)', raw_lower)
        if fer:
            val = float(fer.group(1))
            if val < 12:
                findings.append(f"🔴 Your **ferritin** ({val} ng/mL) is **very low** — this means your iron stores are depleted. Iron is essential for making red blood cells.")

    # Recommendations
    if "statin" in raw_lower or "atorvastatin" in raw_lower:
        advice_items.append("💊 Your doctor has recommended a **statin medication** to lower cholesterol. Take it as prescribed.")
    if "iron" in raw_lower or "ferritin" in raw_lower:
        advice_items.append("🥩 Eat **iron-rich foods**: red meat, lentils, spinach, fortified cereals. Take iron supplements if prescribed.")
    if "mediterranean" in raw_lower or "low-fat" in raw_lower:
        advice_items.append("🥗 Follow a **heart-healthy diet**: less fried food, more vegetables, olive oil, fish, and whole grains.")
    if "aerobic" in raw_lower or "physical activity" in raw_lower or "exercise" in raw_lower:
        advice_items.append("🏃 **Exercise regularly** — aim for 30 minutes of brisk walking or cycling, 5 days a week.")
    if "repeat" in raw_lower or "follow-up" in raw_lower:
        advice_items.append("📅 **Follow up** with your doctor as recommended for repeat testing.")

    if not findings:
        findings.append("ℹ️ No specific abnormal values were automatically detected. Please review with your doctor.")

    return findings, advice_items


def show():
    st.markdown('<p class="section-title">📄 Medical Report Simplifier</p>', unsafe_allow_html=True)
    st.markdown("Upload or paste a complex medical report. Our NLP engine will translate it into plain language.")

    tab1, tab2 = st.tabs(["📋 Paste / Sample Report", "📁 Upload PDF Report"])

    with tab1:
        sample_choice = st.selectbox("Try a sample report:", ["-- None --"] + list(SAMPLE_REPORTS.keys()))
        if sample_choice != "-- None --":
            report_text = st.text_area("Report Text:", value=SAMPLE_REPORTS[sample_choice], height=220)
        else:
            report_text = st.text_area("Paste your medical report here:", height=220,
                                        placeholder="Paste lab results, discharge summary, or any clinical report...")

        if st.button("🔍 Simplify Report", use_container_width=True):
            if report_text.strip():
                findings, advice = simplify_report(report_text)

                st.markdown("---")
                st.markdown("### 🩺 What Your Report Means — In Plain English")

                st.markdown("#### 📌 Key Findings:")
                for f in findings:
                    st.markdown(f)

                if advice:
                    st.markdown("#### 💡 What You Should Do:")
                    for a in advice:
                        st.markdown(a)

                st.markdown("""
                <div class="alert-amber">
                ⚠️ <b>Remember:</b> This simplification is generated by AI to help you understand your report. 
                Always discuss your results with your doctor before making any health decisions.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Please paste a report or select a sample.")

    with tab2:
        uploaded = st.file_uploader("Upload a medical PDF report", type=["pdf"])
        if uploaded:
            st.info("📄 PDF uploaded successfully. In production, pdfplumber/PyMuPDF extracts text for NLP processing.")
            st.markdown("""
            <div class="alert-blue">
            <b>Production Flow:</b><br>
            1. PDF text extracted via <code>pdfplumber</code><br>
            2. Text cleaned and normalized with <code>spaCy</code><br>
            3. NLP pipeline detects abnormal values and generates plain-English summary<br>
            4. Output shown to patient with visual indicators
            </div>
            """, unsafe_allow_html=True)
