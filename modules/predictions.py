import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
import os
import uuid
from datetime import datetime
from modules.db import get_verified_doctors

# Path to your medical dataset
DATASET_PATH = r"C:\Users\Shaheryar\Downloads\nlp_medora_prototype_v4\nlp_medora\data\disease_dataset.csv"

@st.cache_resource
def load_and_train_model():
    """Loads the dataset and trains a Logistic Regression model once."""
    if not os.path.exists(DATASET_PATH):
        return None, None
    
    df = pd.read_csv(DATASET_PATH)
    X = df.drop("disease", axis=1)
    y = df["disease"]
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    
    return model, list(X.columns)

def show():
    st.markdown('<p class="section-title">🔬 AI Disease Prediction</p>', unsafe_allow_html=True)
    st.write("Our AI model analyzes your symptoms against clinical datasets to identify potential health risks.")

    # 1. Load Model
    model, ALL_SYMPTOMS = load_and_train_model()

    if model is None:
        st.error(f"Dataset not found at {DATASET_PATH}. Please check the file path.")
        return

    # 2. Symptom Selection UI
    st.markdown("#### Select Symptoms You Are Experiencing:")
    cols = st.columns(3)
    selected_symptoms = []
    
    for i, symptom in enumerate(ALL_SYMPTOMS):
        clean_name = symptom.replace('_', ' ').title()
        if cols[i % 3].checkbox(clean_name, key=f"pred_{symptom}"):
            selected_symptoms.append(symptom)

    st.divider()

    # 3. Run Diagnostic Logic
    prediction = None
    confidence = 0

    if st.button("🔍 Run AI Diagnostic", use_container_width=True):
        if len(selected_symptoms) < 1:
            st.warning("⚠️ Please select at least one symptom for analysis.")
        else:
            # Prepare data
            input_vector = [1 if sym in selected_symptoms else 0 for sym in ALL_SYMPTOMS]
            
            # Predict
            prediction = model.predict([input_vector])[0]
            probabilities = model.predict_proba([input_vector])[0]
            confidence = max(probabilities) * 100

            # Store result in session state to use for doctor review
            st.session_state.last_prediction = {
                "prediction": prediction,
                "confidence": confidence,
                "symptoms": selected_symptoms
            }

            # Display Results
            st.markdown(f"""
            <div class="alert-blue">
                <h3>🩺 Predicted Condition: {prediction}</h3>
                <p>Based on our trained patterns, your symptoms most closely align with this condition.</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([2, 1])
            with col1:
                st.write("### Analysis Details")
                st.write(f"**Symptoms Matched:** {len(selected_symptoms)}")
                st.write("**Model Type:** Logistic Regression Classifier")
                st.info("💡 **Next Steps:** Please share this result with a doctor below.")

            with col2:
                # Confidence gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=confidence,
                    title={'text': "Confidence %"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#2c5364"},
                        'steps': [
                            {'range': [0, 50], 'color': "#fff0f0"},
                            {'range': [50, 80], 'color': "#fffbf0"},
                            {'range': [80, 100], 'color': "#f0faf0"}
                        ],
                    }
                ))
                fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

    if "last_prediction" in st.session_state:
        st.divider()
        st.markdown("#### 📩 Send for Doctor Review")
        st.caption("Choose a doctor from the list below, then send your AI result for review.")

        doctors = get_verified_doctors(st.session_state.get("users_db", {}))

        if not doctors:
            st.warning("No verified doctors are available right now. Please try again later.")
        else:
            st.markdown("##### Available Doctors")
            doctor_rows = []
            for doc in doctors:
                hospital = doc["hospital"] or "—"
                doctor_rows.append({
                    "Doctor": doc["name"],
                    "Specialty": doc["specialty"],
                    "Hospital / Clinic": hospital,
                })
            st.dataframe(pd.DataFrame(doctor_rows), use_container_width=True, hide_index=True)

            doctor_labels = [
                f"{doc['name']} — {doc['specialty']}"
                + (f" ({doc['hospital']})" if doc["hospital"] else "")
                for doc in doctors
            ]
            selected_idx = st.selectbox(
                "Select a doctor",
                range(len(doctors)),
                format_func=lambda i: doctor_labels[i],
                key="selected_doctor_idx",
            )
            selected_doctor = doctors[selected_idx]

            if st.button("📤 Send to Selected Doctor", use_container_width=True):
                if "prediction_requests" not in st.session_state:
                    st.session_state.prediction_requests = []

                data = st.session_state.last_prediction

                request = {
                    "id": f"REQ-{str(uuid.uuid4())[:8].upper()}",
                    "patient_name": st.session_state.get("username", "Guest"),
                    "patient_email": st.session_state.get("user_email", "unknown@demo.com"),
                    "ai_prediction": data["prediction"],
                    "ai_confidence": round(data["confidence"], 1),
                    "symptoms": data["symptoms"],
                    "status": "Pending",
                    "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "assigned_doctor": selected_doctor["name"],
                    "assigned_doctor_email": selected_doctor["email"],
                    "doctor_name": "",
                    "doctor_note": "",
                    "final_diagnosis": "",
                    "severity": "",
                }

                st.session_state.prediction_requests.append(request)
                st.success(
                    f"✅ Sent Request {request['id']} to **{selected_doctor['name']}**!"
                )