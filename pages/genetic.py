import streamlit as st
import pandas as pd
from services.genetic_test_predictor import train_genetic_model

def show():
    st.header("🧬 Genetic Test Recommendation")
    
    # 1. Load the "Brain"
    clf, encoders, feature_columns = train_genetic_model()

    with st.form("genetic_test_form"):
        age = st.number_input("Age", 1, 120, 30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        parental_history = st.radio("Parental History of Disease", ["Yes", "No"])
        sibling_history = st.radio("Sibling History of Disease", ["Yes", "No"])
        num_relatives = st.number_input("Number of Relatives with Disease", 0, 10, 0)
        known_mutation = st.radio("Known Genetic Mutation in Family", ["Yes", "No"])
        early_onset = st.radio("Early Onset Cases in Family", ["Yes", "No"])
        env_risk = st.selectbox("Environmental Risk Exposure", ["Low", "Moderate", "High"])

        submitted = st.form_submit_button("🔍 Predict Genetic Test Need")
        if submitted:
        user_data = {
            'Age': age,
            'Gender': gender,
            'Parental History': parental_history,
            'Sibling History': sibling_history,
            'Number of Relatives with Disease': num_relatives,
            'Known Genetic Mutation': known_mutation,
            'Early Onset Cases in Family': early_onset,
            'Environmental Risk Exposure': env_risk
        }
        
        input_df = pd.DataFrame([user_data])

        for col in encoders:
            if col in input_df.columns:
                input_df[col] = encoders[col].transform(input_df[col])

        input_df = input_df[feature_columns]

        prediction = clf.predict(input_df)[0]
        probability = clf.predict_proba(input_df)[0][1] * 100

        if prediction == 1:
            st.error(f"⚠️ High Priority: Genetic testing recommended. (AI Confidence: {probability:.1f}%)")
        else:
            st.success(f"✅ Low Priority: Testing may not be necessary. (AI Confidence: {100-probability:.1f}%)")
