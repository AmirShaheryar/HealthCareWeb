import streamlit as st
import plotly.graph_objects as go

DISEASE_MAP = {
    frozenset(["fever", "cough", "fatigue", "sore throat"]): {
        "disease": "Influenza (Flu)", "confidence": 88,
        "description": "Viral respiratory illness. Most common in winter months.",
        "advice": "Rest, fluids, paracetamol. Antiviral if within 48hr of onset.",
        "urgency": "⚠️ Moderate"
    },
    frozenset(["fever", "cough", "shortness of breath", "fatigue"]): {
        "disease": "COVID-19 / Pneumonia", "confidence": 82,
        "description": "Lower respiratory tract infection — viral or bacterial.",
        "advice": "PCR test recommended. Monitor oxygen saturation. Seek care if SpO₂ <94%.",
        "urgency": "🔴 Urgent"
    },
    frozenset(["chest pain", "shortness of breath", "sweating", "nausea"]): {
        "disease": "Acute Coronary Syndrome (Heart Attack)", "confidence": 91,
        "description": "Blockage of coronary artery — medical emergency.",
        "advice": "Call emergency services IMMEDIATELY. Take aspirin 325mg if available.",
        "urgency": "🚨 Emergency"
    },
    frozenset(["headache", "fever", "stiff neck", "sensitivity to light"]): {
        "disease": "Meningitis", "confidence": 79,
        "description": "Inflammation of brain/spinal cord membranes — potentially life-threatening.",
        "advice": "Emergency hospital visit required. Do not delay.",
        "urgency": "🚨 Emergency"
    },
    frozenset(["increased thirst", "frequent urination", "fatigue", "blurred vision"]): {
        "disease": "Diabetes Mellitus (Type 2)", "confidence": 85,
        "description": "Insufficient insulin or insulin resistance.",
        "advice": "Fasting blood glucose test. HbA1c test. Lifestyle modification.",
        "urgency": "⚠️ Moderate"
    },
    frozenset(["joint pain", "swelling", "morning stiffness", "fatigue"]): {
        "disease": "Rheumatoid Arthritis", "confidence": 76,
        "description": "Autoimmune inflammatory joint disease.",
        "advice": "Rheumatology referral. Anti-inflammatory medication. Physiotherapy.",
        "urgency": "⚠️ Moderate"
    },
    frozenset(["abdominal pain", "nausea", "vomiting", "diarrhea"]): {
        "disease": "Gastroenteritis / Food Poisoning", "confidence": 84,
        "description": "Inflammation of gastrointestinal tract, often viral or bacterial.",
        "advice": "ORS for rehydration. Bland diet. Antibiotics only if bacterial confirmed.",
        "urgency": "✅ Mild–Moderate"
    },
    frozenset(["persistent cough", "weight loss", "night sweats", "blood in sputum"]): {
        "disease": "Tuberculosis (TB)", "confidence": 87,
        "description": "Bacterial infection of the lungs (Mycobacterium tuberculosis).",
        "advice": "Immediate chest X-ray and sputum culture. Notify public health authority.",
        "urgency": "🔴 Urgent"
    },
    frozenset(["sadness", "fatigue", "poor sleep", "loss of interest"]): {
        "disease": "Major Depressive Disorder", "confidence": 80,
        "description": "Persistent depressive mood affecting daily functioning.",
        "advice": "Mental health consultation. Psychotherapy (CBT). Consider medication.",
        "urgency": "⚠️ Moderate"
    },
}

ALL_SYMPTOMS = sorted(set(s for combo in DISEASE_MAP.keys() for s in combo))

def predict_disease(selected):
    selected_set = frozenset(s.lower() for s in selected)
    best_match = None
    best_overlap = 0
    best_confidence = 0

    for symptom_combo, data in DISEASE_MAP.items():
        overlap = len(selected_set & symptom_combo)
        if overlap > best_overlap:
            best_overlap = overlap
            total_symptoms = len(symptom_combo)
            adjusted_conf = int(data["confidence"] * (overlap / total_symptoms))
            best_match = data.copy()
            best_match["confidence"] = adjusted_conf
            best_match["matched"] = overlap
            best_match["total"] = total_symptoms
            best_confidence = adjusted_conf

    return best_match

def show():
    st.markdown('<p class="section-title">🔬 AI Disease Prediction</p>', unsafe_allow_html=True)
    st.markdown("Select your symptoms for an AI-powered disease risk assessment using knowledge-base mapping.")

    tab1, tab2 = st.tabs(["🧠 Symptom-to-Disease Predictor", "📝 Free-Text Symptom Analysis (RAG)"])

    with tab1:
        st.markdown("#### Select All Symptoms You Are Currently Experiencing:")

        # Group symptoms visually
        cols = st.columns(3)
        selected_symptoms = []
        for i, symptom in enumerate(ALL_SYMPTOMS):
            if cols[i % 3].checkbox(symptom.title(), key=f"sym_{symptom}"):
                selected_symptoms.append(symptom)

        st.divider()

        if st.button("🔍 Analyse Symptoms", use_container_width=True):
            if len(selected_symptoms) < 2:
                st.warning("Please select at least 2 symptoms for accurate prediction.")
            else:
                result = predict_disease(selected_symptoms)
                if result and result["confidence"] > 10:
                    # Urgency alert
                    urgency = result["urgency"]
                    if "Emergency" in urgency:
                        color = "alert-red"
                    elif "Urgent" in urgency:
                        color = "alert-red"
                    elif "Moderate" in urgency:
                        color = "alert-amber"
                    else:
                        color = "alert-green"

                    st.markdown(f"""
                    <div class="{color}">
                    <h3>🩺 Most Likely Condition: {result['disease']}</h3>
                    <b>Urgency:</b> {urgency} &nbsp;|&nbsp; <b>Symptom Match:</b> {result['matched']}/{result['total']} symptoms matched
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**📋 Description:** {result['description']}")
                        st.markdown(f"**💊 Recommended Action:** {result['advice']}")
                        st.markdown("""
                        <div class="alert-amber">
                        ⚠️ <b>Medical Disclaimer:</b> This AI prediction is for informational guidance only. 
                        It is NOT a clinical diagnosis. Always consult a licensed physician.
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        # Confidence gauge
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=result["confidence"],
                            title={"text": "Match Confidence (%)"},
                            gauge={
                                "axis": {"range": [0, 100]},
                                "bar": {"color": "#2c5364"},
                                "steps": [
                                    {"range": [0,  40], "color": "#ffcdd2"},
                                    {"range": [40, 70], "color": "#fff9c4"},
                                    {"range": [70,100], "color": "#c8e6c9"},
                                ]
                            }
                        ))
                        fig.update_layout(height=220, margin=dict(l=5, r=5, t=30, b=5), paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No strong match found for the selected combination. Try selecting more specific symptoms or consult a doctor.")

    with tab2:
        st.markdown("#### 📝 Free-Text Symptom Extraction (RAG Simulation)")
        st.markdown("Type a description of how you feel. The system will extract symptoms and match to conditions.")

        free_text = st.text_area("Describe your symptoms in natural language:",
                                  height=120,
                                  placeholder="e.g. I have been having fever for 3 days, feeling very tired and coughing a lot. My throat is also sore.")

        if st.button("🔎 Extract & Predict"):
            if free_text.strip():
                text_lower = free_text.lower()
                extracted = [s for s in ALL_SYMPTOMS if s.lower() in text_lower]

                # Also check common synonyms
                synonym_map = {
                    "tired": "fatigue", "exhausted": "fatigue", "temperature": "fever",
                    "throwing up": "nausea", "vomit": "nausea", "breathless": "shortness of breath",
                    "can't breathe": "shortness of breath", "dizzy": "headache",
                    "depressed": "sadness", "sad": "sadness", "down": "sadness",
                    "pee a lot": "frequent urination", "thirsty": "increased thirst",
                }
                for word, symptom in synonym_map.items():
                    if word in text_lower and symptom not in extracted:
                        extracted.append(symptom)

                if extracted:
                    st.markdown(f"**🔍 Extracted Symptoms:** {', '.join([s.title() for s in extracted])}")
                    result = predict_disease(extracted)
                    if result and result["confidence"] > 10:
                        st.markdown(f"""
                        <div class="alert-blue">
                        <b>🤖 RAG Prediction:</b> Based on your description, the most likely condition is 
                        <b>{result['disease']}</b> (confidence: {result['confidence']}%)<br>
                        <b>Action:</b> {result['advice']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Could not map to a known condition. Please consult a doctor.")
                else:
                    st.warning("No recognisable symptoms found in text. Try describing more specifically.")
            else:
                st.warning("Please enter a description.")
