import streamlit as st
from datetime import datetime

st.markdown("""
<style>
.stTabs [data-baseweb="tab"] { color: #1a1a2e !important; }
.stTabs [aria-selected="true"] { background: #2c5364 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

SAMPLE_PATIENTS = [
    {"id": "P001", "name": "Ali Raza", "age": 45, "condition": "Type 2 Diabetes",
     "last_visit": "2024-11-10", "bp": "142/88", "glucose": 182, "status": "Pending Review"},
    {"id": "P002", "name": "Ayesha Malik", "age": 32, "condition": "Hypertension",
     "last_visit": "2024-11-08", "bp": "155/95", "glucose": 96, "status": "Pending Review"},
    {"id": "P003", "name": "Usman Khan", "age": 58, "condition": "Chest Pain — Rule out ACS",
     "last_visit": "2024-11-15", "bp": "148/92", "glucose": 110, "status": "Verified"},
]

def show():
    if st.session_state.user_role != "Doctor":
        st.warning("🚫 This section is restricted to Doctors only.")
        return

    st.markdown('<p class="section-title">🩺 Doctor Clinical Panel</p>', unsafe_allow_html=True)
    st.markdown(f"Welcome, **{st.session_state.username}**. Review and verify AI-generated patient predictions.")

    tab1, tab2, tab3 = st.tabs(["👥 Patient List", "🔬 Review AI Prediction", "📋 Write Clinical Note"])

    with tab1:
        st.markdown("#### Active Patient Cases")
        for p in SAMPLE_PATIENTS:
            status_color = "alert-amber" if p["status"] == "Pending Review" else "alert-green"
            status_icon = "⏳" if p["status"] == "Pending Review" else "✅"
            label = f"{status_icon} {p['name']}  |  {p['condition']}  |  {p['status']}"
            with st.expander(label):
                col1, col2, col3 = st.columns(3)
                col1.metric("Age", p["age"])
                col2.metric("Blood Pressure", p["bp"])
                col3.metric("Blood Glucose", f"{p['glucose']} mg/dL")
                st.markdown(f'<div class="{status_color}">Status: {p["status"]} | Last Visit: {p["last_visit"]}</div>',
                            unsafe_allow_html=True)
                if p["status"] == "Pending Review":
                    if st.button(f"✅ Mark as Verified — {p['id']}", key=f"verify_{p['id']}"):
                        for patient in SAMPLE_PATIENTS:
                            if patient["id"] == p["id"]:
                                patient["status"] = "Verified"
                        st.success(f"Patient {p['name']} prediction verified!")
                        st.rerun()

    with tab2:
        st.markdown("#### 🤖 AI-Generated Prediction Review")
        patient_choice = st.selectbox("Select Patient", [p["name"] for p in SAMPLE_PATIENTS])
        patient = next(p for p in SAMPLE_PATIENTS if p["name"] == patient_choice)

        st.markdown(f"""
        <div class="card">
        <b>Patient:</b> {patient['name']} | Age: {patient['age']}<br>
        <b>AI Predicted Condition:</b> {patient['condition']}<br>
        <b>Vitals:</b> BP {patient['bp']} | Glucose {patient['glucose']} mg/dL<br>
        <b>Status:</b> {patient['status']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Doctor's Assessment:**")
        agree = st.radio("Do you agree with the AI prediction?", ["✅ Agree", "❌ Disagree — provide alternative", "⚠️ Partially agree"])
        if "Disagree" in agree or "Partially" in agree:
            alt_diagnosis = st.text_input("Alternative / Corrected Diagnosis:")
        notes = st.text_area("Clinical Notes / Additional Comments:", height=100)
        severity = st.select_slider("Severity", ["Low", "Moderate", "High", "Critical"])

        if st.button("💾 Submit Clinical Review"):
            st.success(f"✅ Clinical review submitted for {patient['name']}. Record updated.")
            if "reviews" not in st.session_state:
                st.session_state.reviews = []
            st.session_state.reviews.append({
                "patient": patient["name"],
                "doctor": st.session_state.username,
                "assessment": agree,
                "severity": severity,
                "notes": notes,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

    with tab3:
        st.markdown("#### 📝 Write Clinical / SOAP Note")
        patient_name = st.text_input("Patient Name:")
        note_type = st.selectbox("Note Type", ["SOAP Note", "Discharge Summary", "Referral Letter", "Progress Note"])
        note_content = st.text_area(f"Write {note_type}:", height=200,placeholder="S: Patient reports...\nO: Vitals stable...\nA: Likely diagnosis...\nP: Plan includes...")
        col1, col2 = st.columns(2)
        if col1.button("💾 Save Note"):
            st.success(f"✅ {note_type} saved for {patient_name}.")
        if col2.button("📤 Mark for Patient Access"):
            st.info("Note marked for patient access (read-only).")