import streamlit as st
import plotly.graph_objects as go
from services import nutrition_service as ns


def show():
    st.title("🥗 AI Nutrition & Budget Planner")

    condition = st.selectbox("Select Condition", ns.get_conditions())
    budget = st.slider("Monthly Budget (PKR)", 2000, 30000, 8000)

    data = ns.get_data(condition)
    st.info(f"🎯 Goal: {data['goal']}")

    # Backend calls
    expensive, budget_items = ns.filter_by_budget(condition, budget)
    ranked = ns.rank_budget_foods(condition)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💸 Expensive")
        for i in expensive:
            tag = "❌" if not i["affordable"] else "⚠️"
            st.write(f"{tag} {i['name']} - PKR {i['price']}")

    with col2:
        st.subheader("✅ Budget Options")
        for i in ranked:
            st.write(f"✔ {i['name']} - PKR {i['price']}")
            if "note" in i:
                st.caption(i["note"])

    # Chart
    fig = go.Figure()
    fig.add_bar(
        name="Expensive",
        x=[i["name"] for i in expensive],
        y=[i["price"] for i in expensive]
    )
    fig.add_bar(
        name="Budget",
        x=[i["name"] for i in budget_items],
        y=[i["price"] for i in budget_items]
    )
    fig.update_layout(barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    # Savings
    savings = ns.calculate_savings(condition)
    st.success(f"💰 You can save PKR {savings}")

    # Best swap
    swap = ns.best_swap(condition)
    st.info(f"🔁 Best Budget Alternative: {swap}")

    # Meal Plan
    st.subheader("🍽️ Daily Meal Plan")
    for meal, food in ns.generate_meal_plan(condition):
        st.write(f"**{meal}:** {food}")

    # AI Advice
    advice = ns.generate_recommendation(condition, budget)
    st.warning(f"🧠 Advice: {advice}")
