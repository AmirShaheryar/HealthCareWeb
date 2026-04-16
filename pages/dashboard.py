import streamlit as st
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
def show():
    st.markdown('<p class="section-title">🏠 Personal Health Dashboard</p>', unsafe_allow_html=True)
    st.markdown(f"**Hello, {st.session_state.username}!** Here's your health summary for today.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("❤️ Heart Rate", "72 bpm", "-3 bpm")
    col2.metric("🩸 Blood Pressure", "118/76", "Normal")
    col3.metric("🏃 Steps Today", "7,432", "+12%")
    col4.metric("😴 Sleep", "7h 20m", "+0h 15m")

    st.divider()

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("#### 📈 Weekly Heart Rate Trend")
        days = [(datetime.today() - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
        hr_values = [68, 72, 75, 70, 74, 71, 72]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days, y=hr_values,
            mode="lines+markers",
            line=dict(color="#2c5364", width=3),
            marker=dict(size=8, color="#2c5364"),
            fill="tozeroy",
            fillcolor="rgba(44,83,100,0.1)"
        ))
        fig.update_layout(
            height=220, margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(range=[50, 100], title="bpm"),
            plot_bgcolor="#fafcff", paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### 🩺 Health Score")
        score = 78
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2c5364"},
                "steps": [
                    {"range": [0, 40],  "color": "#ffcdd2"},
                    {"range": [40, 70], "color": "#fff9c4"},
                    {"range": [70, 100],"color": "#c8e6c9"},
                ],
            }
        ))
        fig2.update_layout(height=220, margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)
