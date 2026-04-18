import streamlit as st
import plotly.graph_objects as go

NUTRITION_DB = {
    "Iron Deficiency / Anaemia": {
        "goal": "Increase iron, B12, and folate intake",
        "expensive": [
            {"name": "Grass-fed Beef",     "price": 1800, "iron": 2.7,  "protein": 26, "unit": "100g"},
            {"name": "Atlantic Salmon",    "price": 1200, "iron": 0.8,  "protein": 20, "unit": "100g"},
            {"name": "Chia Seeds",         "price": 900,  "iron": 7.7,  "protein": 17, "unit": "100g"},
        ],
        "budget": [
            {"name": "Lentils (Masoor Dal)","price": 120,  "iron": 7.5,  "protein": 25, "unit": "100g", "note": "Nearly identical iron to chia seeds at 1/7 the cost!"},
            {"name": "Spinach (Palak)",     "price": 60,   "iron": 2.7,  "protein": 2.9,"unit": "100g", "note": "Same iron as beef, plus rich in folate"},
            {"name": "Chicken Liver",       "price": 200,  "iron": 11.0, "protein": 20, "unit": "100g", "note": "3x more iron than beef at much lower cost"},
            {"name": "Eggs",                "price": 180,  "iron": 1.8,  "protein": 13, "unit": "100g", "note": "Excellent B12 source, budget-friendly protein"},
        ]
    },
    "High Cholesterol": {
        "goal": "Reduce LDL cholesterol, increase omega-3 and fibre",
        "expensive": [
            {"name": "Wild Salmon",         "price": 1500, "fiber": 0,    "omega3": 2.2, "unit": "100g"},
            {"name": "Avocado",             "price": 500,  "fiber": 6.7,  "omega3": 0.1, "unit": "100g"},
            {"name": "Walnuts",             "price": 1200, "fiber": 6.7,  "omega3": 9.1, "unit": "100g"},
        ],
        "budget": [
            {"name": "Sardines (canned)",   "price": 250,  "fiber": 0,    "omega3": 2.0, "unit": "100g", "note": "Nearly same omega-3 as wild salmon at 1/6 price!"},
            {"name": "Flaxseeds",           "price": 180,  "fiber": 27.3, "omega3": 22.8,"unit": "100g", "note": "Highest omega-3 per rupee — grind before eating"},
            {"name": "Oats",                "price": 90,   "fiber": 10.6, "omega3": 0.1, "unit": "100g", "note": "Beta-glucan in oats actively lowers LDL cholesterol"},
            {"name": "Chickpeas (Chanay)",  "price": 100,  "fiber": 12.5, "omega3": 0.1, "unit": "100g", "note": "High fibre, low cost — a cholesterol-lowering staple"},
        ]
    },
    "Diabetes / Blood Sugar Control": {
        "goal": "Low glycaemic index foods to stabilise blood sugar",
        "expensive": [
            {"name": "Quinoa",              "price": 1200, "gi": 53, "protein": 14, "unit": "100g"},
            {"name": "Almonds",             "price": 2000, "gi": 15, "protein": 21, "unit": "100g"},
            {"name": "Blueberries",         "price": 1500, "gi": 40, "protein": 0.7,"unit": "100g"},
        ],
        "budget": [
            {"name": "Brown Rice",          "price": 150,  "gi": 55, "protein": 2.6, "unit": "100g", "note": "Lower GI than white rice, widely available, affordable"},
            {"name": "Peanuts",             "price": 200,  "gi": 14, "protein": 26,  "unit": "100g", "note": "Same low GI as almonds at 1/10 the price!"},
            {"name": "Guava (Amrood)",      "price": 60,   "gi": 36, "protein": 2.6, "unit": "100g", "note": "Low GI, high fibre — better than imported berries"},
            {"name": "Barley (Jau)",        "price": 80,   "gi": 28, "protein": 12.5,"unit": "100g", "note": "Very low GI, high soluble fibre — excellent for T2DM"},
        ]
    },
    "General Fitness & Muscle Building": {
        "goal": "High protein, balanced macros for muscle recovery",
        "expensive": [
            {"name": "Whey Protein",        "price": 3000, "protein": 80, "carbs": 10, "unit": "100g"},
            {"name": "Greek Yogurt",        "price": 600,  "protein": 10, "carbs": 4,  "unit": "100g"},
            {"name": "Tuna (imported)",     "price": 800,  "protein": 30, "carbs": 0,  "unit": "100g"},
        ],
        "budget": [
            {"name": "Eggs",                "price": 180,  "protein": 13, "carbs": 1.1,"unit": "100g", "note": "Complete protein source with all amino acids"},
            {"name": "Dahi (Yogurt)",       "price": 120,  "protein": 3.5,"carbs": 4.7,"unit": "100g", "note": "Local probiotic yogurt — same benefit as Greek yogurt"},
            {"name": "Lentils (Dal)",       "price": 120,  "protein": 25, "carbs": 60, "unit": "100g", "note": "Excellent plant protein + complex carbs for energy"},
            {"name": "Local Tuna/Mackerel", "price": 350,  "protein": 26, "carbs": 0,  "unit": "100g", "note": "Same protein as imported tuna at less than half price"},
        ]
    },
}

def show():
    st.markdown('<p class="section-title">🥗 Price-Aware Nutrition Suggestions</p>', unsafe_allow_html=True)
    st.markdown("Get budget-friendly food alternatives with identical nutritional profiles to expensive superfoods.")

    col1, col2 = st.columns(2)
    with col1:
        condition = st.selectbox("🎯 Select Health Goal / Condition", list(NUTRITION_DB.keys()))
    with col2:
        budget = st.slider("💰 Monthly Food Budget (PKR)", 2000, 30000, 8000, step=500)

    data = NUTRITION_DB[condition]
    st.markdown(f'<div class="alert-blue">🎯 <b>Goal:</b> {data["goal"]}</div>', unsafe_allow_html=True)
    st.divider()

    col_exp, col_bud = st.columns(2)

    with col_exp:
        st.markdown("### 💸 Expensive Options")
        for item in data["expensive"]:
            price = item["price"]
            affordable = price <= budget / 30  # daily budget check
            st.markdown(f"""
            <div class="card" style="border-left: 4px solid {'#e53935' if not affordable else '#aaa'};">
            <b>{item['name']}</b><br>
            💵 <b>PKR {price}</b> / {item['unit']}<br>
            {'⛔ Over daily budget' if not affordable else ''}
            </div>
            """, unsafe_allow_html=True)

    with col_bud:
        st.markdown("### ✅ Budget-Friendly Alternatives")
        total_savings = 0
        for item in data["budget"]:
            price = item["price"]
            note  = item.get("note", "")
            exp_price = data["expensive"][0]["price"] if data["expensive"] else price
            savings = max(0, exp_price - price)
            total_savings += savings
            st.markdown(f"""
            <div class="card" style="border-left: 4px solid #43a047;">
            <b>{item['name']}</b><br>
            💚 <b>PKR {price}</b> / {item['unit']}<br>
            💡 {note}
            </div>
            """, unsafe_allow_html=True)

    # ── Savings visualization ──────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📊 Cost Comparison")
    names_exp = [i["name"] for i in data["expensive"]]
    prices_exp = [i["price"] for i in data["expensive"]]
    names_bud = [i["name"] for i in data["budget"]]
    prices_bud = [i["price"] for i in data["budget"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Expensive Options", x=names_exp, y=prices_exp, marker_color="#e53935"))
    fig.add_trace(go.Bar(name="Budget Alternatives", x=names_bud, y=prices_bud, marker_color="#43a047"))
    fig.update_layout(
        barmode="group", height=300,
        title="Price Comparison (PKR per 100g)",
        plot_bgcolor="#fafcff", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Sample Meal Plan ────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🍽️ Sample Budget Meal Plan")
    meal_plans = {
        "Iron Deficiency / Anaemia": [
            ("Breakfast", "2 boiled eggs + spinach omelette with whole wheat roti"),
            ("Lunch", "Masoor dal with brown rice + salad"),
            ("Snack", "Handful of peanuts or roasted chanay"),
            ("Dinner", "Chicken liver curry or beef stew with vegetables"),
        ],
        "High Cholesterol": [
            ("Breakfast", "Oatmeal with flaxseed + guava"),
            ("Lunch", "Sardines with brown rice + tomato salad"),
            ("Snack", "Chickpea chaat (unsalted)"),
            ("Dinner", "Grilled chicken with steamed vegetables"),
        ],
        "Diabetes / Blood Sugar Control": [
            ("Breakfast", "Barley porridge + 2 boiled eggs"),
            ("Lunch", "Brown rice + lentil dal + salad"),
            ("Snack", "Guava slices + peanuts"),
            ("Dinner", "Grilled fish + stir-fried vegetables"),
        ],
        "General Fitness & Muscle Building": [
            ("Breakfast", "Eggs scramble + whole wheat bread + dahi"),
            ("Lunch", "Chicken breast + lentils + salad"),
            ("Snack", "Peanut butter on whole wheat toast"),
            ("Dinner", "Mackerel curry + brown rice + vegetables"),
        ],
    }

    plan = meal_plans.get(condition, [])
    for meal, desc in plan:
        col_m, col_d = st.columns([1, 4])
        col_m.markdown(f"**{meal}**")
        col_d.markdown(desc)

    monthly_estimate = sum(i["price"] * 3 for i in data["budget"]) * 30 // 100
    st.markdown(f"""
    <div class="alert-green">
    💰 <b>Estimated Monthly Food Cost (Budget Plan):</b> PKR {monthly_estimate:,} 
    — well within your PKR {budget:,} budget!
    </div>
    """, unsafe_allow_html=True)
