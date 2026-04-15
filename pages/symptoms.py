import streamlit as st

SYMPTOM_DB = {
    "Fever": {
        "description": "Elevated body temperature above 38°C (100.4°F).",
        "conditions": ["Common Cold", "Influenza", "COVID-19", "Malaria", "Bacterial Infection"],
        "advice": "Rest, stay hydrated, take paracetamol. Seek doctor if >39.5°C or lasting >3 days.",
        "lifestyle": "Avoid strenuous activity. Drink 8–10 glasses of water daily.",
        "severity": "⚠️ Moderate"
    },
    "Headache": {
        "description": "Pain or discomfort in the head or neck region.",
        "conditions": ["Tension Headache", "Migraine", "Dehydration", "Hypertension", "Sinusitis"],
        "advice": "Rest in a dark room. Take OTC pain reliever. Track triggers (stress, screen time).",
        "lifestyle": "Maintain regular sleep. Reduce caffeine. Stay hydrated.",
        "severity": "✅ Mild"
    },
    "Chest Pain": {
        "description": "Discomfort, tightness or pain in the chest area.",
        "conditions": ["Angina", "Heart Attack", "GERD", "Costochondritis", "Anxiety"],
        "advice": "⚠️ Seek IMMEDIATE medical attention if severe or radiating to arm/jaw.",
        "lifestyle": "Reduce fatty foods, quit smoking, manage stress.",
        "severity": "🔴 Critical – Seek Emergency Care"
    },
    "Shortness of Breath": {
        "description": "Difficulty breathing or feeling of insufficient air.",
        "conditions": ["Asthma", "COPD", "Heart Failure", "Anemia", "Anxiety"],
        "advice": "Use prescribed inhaler if asthmatic. Seek care if sudden onset.",
        "lifestyle": "Avoid triggers (dust, smoke). Practice diaphragmatic breathing.",
        "severity": "⚠️ Moderate–Serious"
    },
    "Fatigue": {
        "description": "Persistent tiredness not relieved by rest.",
        "conditions": ["Anemia", "Hypothyroidism", "Diabetes", "Depression", "Sleep Apnea"],
        "advice": "Get blood work done. Maintain consistent sleep schedule.",
        "lifestyle": "Exercise regularly, eat iron-rich foods, limit alcohol.",
        "severity": "✅ Mild–Moderate"
    },
    "Nausea": {
        "description": "Feeling of unease in the stomach with urge to vomit.",
        "conditions": ["Gastroenteritis", "Food Poisoning", "Migraine", "Pregnancy", "Medication Side Effect"],
        "advice": "Eat bland food (BRAT diet). Stay hydrated with clear fluids.",
        "lifestyle": "Avoid spicy/fatty food. Eat small, frequent meals.",
        "severity": "✅ Mild"
    },
    "Joint Pain": {
        "description": "Aching or soreness in joints.",
        "conditions": ["Arthritis", "Gout", "Lupus", "Viral Infection", "Injury"],
        "advice": "Apply ice/heat. OTC anti-inflammatories (ibuprofen). Physiotherapy if chronic.",
        "lifestyle": "Low-impact exercise (swimming). Maintain healthy weight.",
        "severity": "⚠️ Moderate"
    },
    "Cough": {
        "description": "Repeated or chronic coughing reflex.",
        "conditions": ["Common Cold", "Flu", "Bronchitis", "Asthma", "Tuberculosis"],
        "advice": "Honey + warm water for mild cough. Seek care if blood in sputum.",
        "lifestyle": "Stay away from smoke/dust. Increase vitamin C intake.",
        "severity": "✅ Mild"
    },
}

def show():
    st.markdown('<p class="section-title">💊 Symptom Information Database</p>', unsafe_allow_html=True)
    st.markdown("Search any symptom to get information, possible conditions, and lifestyle advice.")

    search = st.text_input("🔍 Search Symptom", placeholder="e.g. Fever, Headache, Chest Pain...")
    
    filtered = {k: v for k, v in SYMPTOM_DB.items() if search.lower() in k.lower()} if search else SYMPTOM_DB

    if not filtered:
        st.warning("No symptoms found. Try a different keyword.")
        return

    for symptom, data in filtered.items():
        with st.expander(f"{symptom}  —  {data['severity']}", expanded=search != ""):
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(f"**📌 Description:** {data['description']}")
                st.markdown("**🩺 Possible Conditions:**")
                for c in data["conditions"]:
                    st.markdown(f"- {c}")
                st.markdown(f"**💡 Medical Advice:** {data['advice']}")
            with col2:
                st.markdown(f"""
                <div class="alert-green">
                <b>🌿 Lifestyle Tips</b><br>{data['lifestyle']}
                </div>
                """, unsafe_allow_html=True)
                sev = data['severity']
                color = "alert-red" if "Critical" in sev or "Serious" in sev else ("alert-amber" if "Moderate" in sev else "alert-green")
                st.markdown(f'<div class="{color}"><b>Severity:</b> {sev}</div>', unsafe_allow_html=True)

    st.divider()
    
    st.markdown("#### 🧩 Multi-Symptom Checker")
    st.caption("Select multiple symptoms you're experiencing:")
    selected = st.multiselect("Your symptoms", list(SYMPTOM_DB.keys()))
    if selected:
        all_conditions = []
        for s in selected:
            all_conditions.extend(SYMPTOM_DB[s]["conditions"])
        from collections import Counter
        top = Counter(all_conditions).most_common(5)
        st.markdown("**🔎 Top Possible Conditions Based on Your Symptoms:**")
        for cond, count in top:
            bar = "🟩" * count + "⬜" * (5 - count)
            st.markdown(f"- **{cond}** {bar} (mentioned in {count} symptom(s))")
        st.markdown("""
        <div class="alert-amber">
        ⚠️ <b>Disclaimer:</b> This is informational only and is NOT a medical diagnosis. 
        Please consult a qualified healthcare professional.
        </div>
        """, unsafe_allow_html=True)
