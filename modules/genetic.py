import streamlit as st
import pandas as pd
# Import the functions from the predictor file
from services.genetic_test_predictor import predict_genetic_test

def show():
    st.markdown("""
        <style>
        .prediction-box {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f9ff;
            border-left: 6px solid #1f77b4;
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("🧬 Genetic Test Recommendation")

    with st.form("genetic_test_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            parental_history = st.radio("Parental History of Disease", ["Yes", "No"])
            sibling_history = st.radio("Sibling History of Disease", ["Yes", "No"])
        
        with col2:
            num_relatives = st.number_input("Number of Relatives with Disease", min_value=0, max_value=10, value=0)
            known_mutation = st.radio("Known Genetic Mutation in Family", ["Yes", "No"])
            early_onset = st.radio("Early Onset Cases in Family", ["Yes", "No"])
            env_risk = st.selectbox("Environmental Risk Exposure", ["Low", "Moderate", "High"])

        submitted = st.form_submit_button("🔍 Predict Genetic Test Need")

    if submitted:
        user_input = {
            'Age': age,
            'Gender': gender,
            'Parental History': parental_history,
            'Sibling History': sibling_history,
            'Number of Relatives with Disease': num_relatives,
            'Known Genetic Mutation': known_mutation,
            'Early Onset Cases in Family': early_onset,
            'Environmental Risk Exposure': env_risk
        }
        
        # Call the prediction function
        result = predict_genetic_test(user_input)

        # Apply different colors based on result
        box_color = "#dcfce7" if "No" in result else "#fee2e2"
        border_color = "#22c55e" if "No" in result else "#ef4444"

        st.markdown(f"""
            <div class="prediction-box" style="background-color: {box_color}; border-left-color: {border_color};">
                <h4>📊 Prediction Result</h4>
                <p style="font-size: 20px;"><strong>{result}</strong></p>
            </div>
        """, unsafe_allow_html=True)

