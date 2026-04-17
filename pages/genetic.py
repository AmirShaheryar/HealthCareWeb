import streamlit as st
import plotly.graph_objects as go
import random

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
    
    with st.form("genetic_test_form"):
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        parental_history = st.radio("Parental History of Disease", ["Yes", "No"])
        sibling_history = st.radio("Sibling History of Disease", ["Yes", "No"])
        num_relatives = st.number_input("Number of Relatives with Disease", min_value=0, max_value=10, value=0)
        known_mutation = st.radio("Known Genetic Mutation in Family", ["Yes", "No"])
        early_onset = st.radio("Early Onset Cases in Family", ["Yes", "No"])
        env_risk = st.selectbox("Environmental Risk Exposure", ["Low", "Moderate", "High"])

        submitted = st.form_submit_button("🔍 Predict Genetic Test Need")

    if submitted:
        # Simple prototype logic (no ML backend)
        risk_score = 0
        
        # Family history factors
        if parental_history == "Yes":
            risk_score += 3
        if sibling_history == "Yes":
            risk_score += 3
        if num_relatives >= 2:
            risk_score += 2
        elif num_relatives >= 1:
            risk_score += 1
            
        # Genetic factors
        if known_mutation == "Yes":
            risk_score += 4
            
        # Early onset indicator
        if early_onset == "Yes":
            risk_score += 2
            
        # Environmental risk
        if env_risk == "High":
            risk_score += 2
        elif env_risk == "Moderate":
            risk_score += 1
            
        # Age factor (older age slightly increases risk)
        if age > 50:
            risk_score += 1
        
        # Determine recommendation based on risk score
        if risk_score >= 7:
            result = "⚠️ **High Priority**: Genetic testing strongly recommended. Please consult with a genetic counselor."
            recommendation_type = "High Priority"
        elif risk_score >= 4:
            result = "📋 **Moderate Priority**: Consider genetic testing. Discuss with your healthcare provider."
            recommendation_type = "Moderate Priority"
        else:
            result = "✅ **Low Priority**: Routine genetic testing may not be necessary based on current information."
            recommendation_type = "Low Priority"
        
        # Display detailed results
        st.markdown(f"""
            <div class="prediction-box">
                <h4>📊 Genetic Test Recommendation</h4>
                <p><strong>{result}</strong></p>
                <hr>
                <p><small>📈 Risk Score: {risk_score}/10<br>
                🏷️ Category: {recommendation_type}<br>
                ℹ️ This is a prototype demonstration. Please consult a healthcare professional for medical advice.</small></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Optional: Show breakdown
        with st.expander("📊 View Risk Factor Breakdown"):
            st.write(f"""
            - **Family History Contribution**: {3 if parental_history == 'Yes' else 0} (Parental) + {3 if sibling_history == 'Yes' else 0} (Sibling) + {min(2, num_relatives)} (Relatives)
            - **Genetic Mutation**: {4 if known_mutation == 'Yes' else 0}
            - **Early Onset**: {2 if early_onset == 'Yes' else 0}
            - **Environmental Risk**: {2 if env_risk == 'High' else 1 if env_risk == 'Moderate' else 0}
            - **Age Factor**: {1 if age > 50 else 0}
            - **Total Risk Score**: {risk_score}/10
            """)
    st.header("🧬 Genetic Test Recommendation")

