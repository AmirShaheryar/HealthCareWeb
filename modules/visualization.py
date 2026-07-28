import streamlit as st
import pandas as pd
from services import vis

def show():
    st.markdown('### 📊 Health vs. Wealth with ML')
    
    # Session State (No storage)
    if "hvw_data" not in st.session_state:
        st.session_state.hvw_data = [
            {"month": "Jan", "steps": 5000, "sleep": 6, "stress": 8, "med_cost": 6000},
            {"month": "Feb", "steps": 6200, "sleep": 6.5, "stress": 7, "med_cost": 4500},
            {"month": "Mar", "steps": 8000, "sleep": 8, "stress": 3, "med_cost": 1500},
        ]

    df = pd.DataFrame(st.session_state.hvw_data)
    tab1, tab2, tab3 = st.tabs(["🚀 ML Analysis", "💰 Savings Calculator", "🌍 Regional Insights"])

    with tab1:
        st.write("#### Predict Your Monthly Expenses")
        with st.form("ml_input"):
            c1, c2, c3 = st.columns(3)
            in_steps = c1.number_input("Avg Daily Steps", 0, 20000, 7000)
            in_sleep = c2.number_input("Avg Sleep (hrs)", 4.0, 12.0, 7.0)
            in_stress = c3.slider("Stress Level", 1, 10, 5)
            
            if st.form_submit_button("Run ML Prediction"):
                # Call Backend ML Logic
                insight = vis.generate_ai_insight(in_steps, in_sleep, in_stress)

                st.markdown(f"""
                <div class="alert-green">
                💡 <b>AI Insight:</b> {insight}
                </div>
                """, unsafe_allow_html=True)
    with tab2:
        st.write("#### 💰 Preventive vs Reactive Calculator")
        c1, c2 = st.columns(2)
        gym = c1.number_input("Monthly Fitness (PKR)", 0, 10000, 2500)
        food = c2.number_input("Healthy Food (PKR)", 0, 10000, 2000)
        checkup = c1.number_input("Annual Checkup (PKR)", 0, 20000, 5000)
        
        annual_prevention = (gym + food) * 12 + checkup
        # Call Backend Chart Logic
        fig, risk = vis.get_comparison_chart(
            annual_prevention,
            in_steps,
            in_sleep,
            in_stress
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"🧠 Your Health Risk Score: {round(risk, 2)}")

    with tab3:
        st.write("#### 🌍 Pakistan Health Insights")
        # Call Backend Insight Logic
        fig = vis.get_pakistan_insights(in_steps, in_stress)
        st.plotly_chart(fig, use_container_width=True)