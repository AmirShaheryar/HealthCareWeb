import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression


# =========================
# 🔹 TAB 1: ML PREDICTION
# =========================
def get_ml_prediction(df, steps, sleep, stress):
    if len(df) < 3:
        return None

    X = df[['steps', 'sleep', 'stress']]
    y = df['med_cost']

    model = LinearRegression()
    model.fit(X, y)

    input_df = pd.DataFrame([[steps, sleep, stress]],columns=['steps', 'sleep', 'stress'])

    prediction = model.predict(input_df)
    return max(0, int(prediction[0]))


# =========================
# 🔹 TAB 2: INTELLIGENT COST MODEL
# =========================
def calculate_health_risk(steps, sleep, stress):
    """Score from 0 (good) to 1 (bad)"""
    step_score = max(0, 1 - steps / 10000)
    sleep_score = abs(7 - sleep) / 7
    stress_score = stress / 10

    return (step_score + sleep_score + stress_score) / 3


def get_dynamic_costs(risk):
    """Adjust disease costs based on risk"""
    base_costs = {
        "Diabetes": 600000,
        "Cardiac": 800000,
        "Obesity": 400000,
        "Cancer": 1200000
    }

    adjusted = {k: int(v * (1 + risk)) for k, v in base_costs.items()}
    return adjusted


def get_comparison_chart(prevention_annual, steps, sleep, stress):
    risk = calculate_health_risk(steps, sleep, stress)
    costs = get_dynamic_costs(risk)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Reactive (Risk Adjusted)",
        x=list(costs.keys()),
        y=list(costs.values())
    ))

    fig.add_trace(go.Bar(
        name="10-Year Prevention",
        x=list(costs.keys()),
        y=[prevention_annual * 10] * len(costs)
    ))

    fig.update_layout(
        barmode="group",
        title=f"Risk Level: {round(risk, 2)}",
        height=320
    )

    return fig, risk


# =========================
# 🔹 TAB 3: SMART INSIGHTS
# =========================
def get_pakistan_insights(user_steps, user_stress):
    cities = ["Lahore", "Karachi", "Islamabad", "Peshawar", "Multan", "Quetta"]

    base_obesity = np.array([28, 31, 22, 19, 25, 18])
    base_income = np.array([65000, 72000, 85000, 48000, 52000, 42000])

    # Adjust based on user lifestyle
    lifestyle_factor = (user_stress / 10) - (user_steps / 15000)

    obesity = base_obesity + lifestyle_factor * 5
    income_effect = base_income / 1000

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Obesity %",
        x=cities,
        y=obesity
    ))

    fig.add_trace(go.Scatter(
        name="Income (×1000)",
        x=cities,
        y=income_effect,
        mode="lines+markers",
        yaxis="y2"
    ))

    fig.update_layout(
        yaxis2=dict(overlaying="y", side="right"),
        height=320,
        title="Lifestyle Impact on Population Health"
    )

    return fig


# =========================
# 🔹 EXTRA: AI INSIGHT TEXT
# =========================
def generate_ai_insight(steps, sleep, stress):
    if stress > 7:
        return "High stress is increasing your future health cost risk."
    elif steps < 5000:
        return "Low physical activity detected. Increasing risk of chronic diseases."
    elif sleep < 6:
        return "Poor sleep may lead to long-term health issues."
    else:
        return "Your lifestyle is balanced. Keep maintaining it!"