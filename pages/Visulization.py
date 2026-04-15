import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def show():
    st.markdown('<p class="section-title">📊 Health vs. Wealth Visualization</p>', unsafe_allow_html=True)
    st.markdown("Explore the relationship between your health metrics and financial wellness.")

    tab1, tab2, tab3 = st.tabs(["📈 Monthly Trends", "💰 Healthcare Cost Estimator", "🌍 Population Insights"])

    with tab1:
        st.markdown("#### Log Your Monthly Health & Finance Data")
        with st.form("hvw_form"):
            c1, c2, c3, c4 = st.columns(4)
            month    = c1.selectbox("Month", ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
            steps    = c2.number_input("Avg Daily Steps", 0, 30000, 7000)
            sleep    = c3.number_input("Avg Sleep (hrs)", 3.0, 12.0, 7.0)
            med_cost = c4.number_input("Medical Expenses (PKR)", 0, 100000, 1500)
            food     = c1.number_input("Food Budget (PKR)", 0, 50000, 8000)
            gym      = c2.number_input("Fitness Expenses (PKR)", 0, 20000, 2000)
            stress   = c3.slider("Stress Level (1–10)", 1, 10, 4)
            weight   = c4.number_input("Weight (kg)", 30.0, 200.0, 72.0)
            if st.form_submit_button("➕ Add Data Point"):
                if "hvw_data" not in st.session_state:
                    st.session_state.hvw_data = []
                st.session_state.hvw_data.append({
                    "month": month, "steps": steps, "sleep": sleep,
                    "med_cost": med_cost, "food": food, "gym": gym,
                    "stress": stress, "weight": weight,
                    "health_score": min(100, int(steps/200 + sleep*5 + (10-stress)*3))
                })
                st.success("✅ Data point added!")

        # Use demo data if none entered
        if "hvw_data" not in st.session_state or not st.session_state.hvw_data:
            demo = [
                {"month": m, "steps": s, "sleep": sl, "med_cost": mc, "food": f,
                 "gym": g, "stress": st_, "weight": w,
                 "health_score": min(100, int(s/200 + sl*5 + (10-st_)*3))}
                for m, s, sl, mc, f, g, st_, w in [
                    ("Jan",6000,6.5,3000,7000,1500,7,74),
                    ("Feb",6500,7.0,2500,7500,2000,6,73),
                    ("Mar",7000,7.2,2000,8000,2000,5,72),
                    ("Apr",8000,7.5,1200,8500,2500,4,71),
                    ("May",9000,7.8,800, 9000,2500,3,70),
                    ("Jun",8500,8.0,600, 9500,3000,3,70),
                ]
            ]
            st.session_state.hvw_data = demo

        df = pd.DataFrame(st.session_state.hvw_data)

        # Chart 1: Health score vs Medical cost
        col_a, col_b = st.columns(2)
        with col_a:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["month"], y=df["health_score"],
                                     mode="lines+markers", name="Health Score",
                                     line=dict(color="#2c5364", width=3), yaxis="y"))
            fig.add_trace(go.Bar(x=df["month"], y=df["med_cost"],
                                  name="Medical Cost (PKR)", marker_color="#e57373",
                                  opacity=0.6, yaxis="y2"))
            fig.update_layout(
                title="Health Score vs Medical Expenses",
                yaxis=dict(title="Health Score", range=[0,100]),
                yaxis2=dict(title="PKR", overlaying="y", side="right"),
                plot_bgcolor="#fafcff", paper_bgcolor="rgba(0,0,0,0)",
                height=300, margin=dict(l=10, r=10, t=40, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            # Pie: spending breakdown
            latest = df.iloc[-1]
            fig2 = go.Figure(go.Pie(
                labels=["Food", "Medical", "Fitness"],
                values=[latest["food"], latest["med_cost"], latest["gym"]],
                hole=0.4,
                marker_colors=["#42a5f5", "#ef5350", "#66bb6a"]
            ))
            fig2.update_layout(title="Health Spending Breakdown", height=300,
                                margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

        # Chart 2: Steps vs Stress
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df["month"], y=df["steps"],
                                   mode="lines+markers", name="Daily Steps", line=dict(color="#43a047")))
        fig3.add_trace(go.Scatter(x=df["month"], y=[s*1000 for s in df["stress"]],
                                   mode="lines+markers", name="Stress ×1000", line=dict(color="#fb8c00", dash="dot")))
        fig3.update_layout(title="Physical Activity vs Stress Level",
                           plot_bgcolor="#fafcff", paper_bgcolor="rgba(0,0,0,0)",
                           height=250, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig3, use_container_width=True)

        # Insight
        if len(df) >= 2:
            first_mc = df.iloc[0]["med_cost"]
            last_mc  = df.iloc[-1]["med_cost"]
            savings  = first_mc - last_mc
            first_hs = df.iloc[0]["health_score"]
            last_hs  = df.iloc[-1]["health_score"]
            if savings > 0:
                st.markdown(f"""
                <div class="alert-green">
                💡 <b>NLP-Medora Insight:</b> Your medical expenses dropped by <b>PKR {savings:,}</b> 
                as your health score improved from <b>{first_hs}</b> to <b>{last_hs}</b>. 
                Preventive health truly saves money!
                </div>
                """, unsafe_allow_html=True)
