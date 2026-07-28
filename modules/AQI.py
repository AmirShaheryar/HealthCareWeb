from __future__ import annotations
import streamlit as st
from datetime import datetime
from typing import Any



def get_aqi_category(aqi: int) -> dict[str, Any]:
    if aqi <= 50:
        return {"label": "Good", "emoji": "🟢", "color": "#1b5e20", "bg": "#f0faf0", "border": "#43a047", "risk": 0}
    if aqi <= 100:
        return {"label": "Moderate", "emoji": "🟡", "color": "#633806", "bg": "#fffbf0", "border": "#fb8c00", "risk": 1}
    if aqi <= 150:
        return {"label": "Unhealthy for Sensitive Groups", "emoji": "🟠", "color": "#712B13", "bg": "#fff3e0", "border": "#ef6c00", "risk": 2}
    if aqi <= 200:
        return {"label": "Unhealthy", "emoji": "🔴", "color": "#791F1F", "bg": "#fff0f0", "border": "#e53935", "risk": 3}
    if aqi <= 300:
        return {"label": "Very Unhealthy", "emoji": "🟣", "color": "#3C3489", "bg": "#ede7f6", "border": "#7b1fa2", "risk": 4}
    return {"label": "Hazardous", "emoji": "⚫", "color": "#4A1B0C", "bg": "#fbe9e7", "border": "#bf360c", "risk": 5}


def get_pollutant_multiplier(pollutant: str) -> float:
    return {
        "PM2.5": 1.4, "PM10": 1.1, "Ozone (O₃)": 1.3,
        "NO₂": 1.2, "SO₂": 1.1, "CO": 1.0,
    }.get(pollutant, 1.0)


def get_genetic_sensitivity(genetic_variants: list[str]) -> dict[str, Any]:
    weights = {"PM2.5": 1.0, "PM10": 1.0, "Ozone (O₃)": 1.0, "NO₂": 1.0, "SO₂": 1.0, "CO": 1.0}
    variant_map = {
        "GSTP1 (oxidative stress sensitivity)": {"PM2.5": 0.5, "Ozone (O₃)": 0.4},
        "ADRB2 (bronchodilation response)": {"Ozone (O₃)": 0.6, "NO₂": 0.3},
        "TNF-α (inflammatory response)": {"PM2.5": 0.4, "PM10": 0.3, "SO₂": 0.3},
        "HLA-DRB1 (immune hypersensitivity)": {"PM2.5": 0.3, "NO₂": 0.4, "SO₂": 0.5},
        "NQO1 (detoxification deficiency)": {"PM2.5": 0.6, "CO": 0.4},
        "ACE (cardiovascular sensitivity)": {"PM2.5": 0.5, "CO": 0.5, "NO₂": 0.3},
        "None / Unknown": {},
    }
    for variant in genetic_variants:
        for poll, add in variant_map.get(variant, {}).items():
            weights[poll] = round(weights[poll] + add, 2)

    total_extra = sum(v - 1.0 for v in weights.values())
    if total_extra >= 2.0:
        level = "High genetic sensitivity"
    elif total_extra >= 0.8:
        level = "Moderate genetic sensitivity"
    else:
        level = "Low / baseline genetic sensitivity"
    return {"weights": weights, "level": level, "total_extra": round(total_extra, 2)}


def get_age_multiplier(age_group: str) -> float:
    return {
        "Child (under 12)": 1.4, "Teen (12–17)": 1.1,
        "Adult (18–60)": 1.0, "Adult (18-60)": 1.0, "Senior (60+)": 1.35,
    }.get(age_group, 1.0)


def get_condition_bonus(conditions: list[str]) -> float:
    bonuses = {"Asthma": 1.5, "COPD": 1.8, "Heart disease": 1.6, "Diabetes": 0.8, "Pregnancy": 1.2, "None": 0.0}
    return sum(bonuses.get(c, 0) for c in conditions)


def get_activity_multiplier(activity: str) -> float:
    return {
        "No outdoor activity": 1.0, "Light walk": 1.3,
        "Moderate exercise": 1.7, "Intense exercise": 2.2,
    }.get(activity, 1.0)


def compute_personal_risk_score(
    aqi: int, pollutant: str, genetic_data: dict[str, Any],
    age_group: str, conditions: list[str], activity: str,
) -> float:
    base = get_aqi_category(aqi)["risk"]
    score = (
        base
        * get_pollutant_multiplier(pollutant)
        * genetic_data["weights"].get(pollutant, 1.0)
        * get_age_multiplier(age_group)
        * get_activity_multiplier(activity)
    ) + get_condition_bonus(conditions)
    return round(min(score, 10.0), 2)


def classify_personal_risk(score: float) -> dict[str, str]:
    if score < 1.5:
        return {"level": "Low risk", "color": "#1b5e20", "bg": "#f0faf0", "border": "#43a047", "icon": "✅"}
    if score < 3.5:
        return {"level": "Moderate risk", "color": "#633806", "bg": "#fffbf0", "border": "#fb8c00", "icon": "⚠️"}
    if score < 6.0:
        return {"level": "High risk", "color": "#791F1F", "bg": "#fff0f0", "border": "#e53935", "icon": "🔴"}
    return {"level": "Critical risk", "color": "#3C3489", "bg": "#ede7f6", "border": "#7b1fa2", "icon": "🚨"}


def get_symptoms_to_watch(pollutant: str, conditions: list[str]) -> list[str]:
    base = {
        "PM2.5": ["Coughing / throat irritation", "Shortness of breath", "Eye irritation", "Chest tightness"],
        "PM10": ["Sneezing / runny nose", "Eye irritation", "Coughing"],
        "Ozone (O₃)": ["Chest pain on deep breath", "Throat irritation", "Worsened asthma", "Headache"],
        "NO₂": ["Coughing", "Wheezing", "Difficulty breathing"],
        "SO₂": ["Nose & throat burning", "Coughing", "Chest tightness"],
        "CO": ["Headache", "Dizziness", "Nausea", "Confusion (high exposure)"],
    }
    extras = {
        "Asthma": ["Asthma attack / wheezing episode"],
        "COPD": ["COPD exacerbation", "Increased mucus"],
        "Heart disease": ["Chest pressure", "Irregular heartbeat"],
        "Pregnancy": ["Dizziness / light-headedness"],
        "Diabetes": ["Unusual fatigue or weakness"],
    }
    symptoms = list(base.get(pollutant, []))
    for c in conditions:
        symptoms += extras.get(c, [])
    return list(dict.fromkeys(symptoms))


def get_action_recommendations(
    score: float, aqi: int, activity: str, conditions: list[str], age_group: str,
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []

    if score >= 6.0:
        actions.append({"text": "Stay indoors and keep all windows closed.", "priority": "high"})
        actions.append({"text": "Use a HEPA air purifier if available indoors.", "priority": "high"})
    elif score >= 3.5:
        actions.append({"text": "Limit outdoor time, especially 10am–4pm (peak pollution hours).", "priority": "medium"})
        if activity in ("Moderate exercise", "Intense exercise"):
            actions.append({"text": "Move your workout indoors today — breathing hard outside multiplies pollutant intake.", "priority": "medium"})
    elif score >= 1.5:
        if activity == "Intense exercise":
            actions.append({"text": "Consider reducing outdoor exercise intensity or duration.", "priority": "low"})
    else:
        actions.append({"text": "Air quality is safe for most outdoor activities today.", "priority": "safe"})

    if aqi > 150:
        actions.append({"text": "Wear an N95/KN95 mask if you must go outside.", "priority": "high"})
    if "Asthma" in conditions and aqi > 100:
        actions.append({"text": "Keep your rescue inhaler accessible at all times today.", "priority": "high"})
    if "COPD" in conditions and aqi > 100:
        actions.append({"text": "Follow your COPD action plan; call your doctor if symptoms worsen.", "priority": "high"})
    if "Heart disease" in conditions and aqi > 100:
        actions.append({"text": "Avoid all strenuous activity and watch for chest discomfort.", "priority": "high"})
    if age_group == "Child (under 12)" and aqi > 100:
        actions.append({"text": "Keep children indoors during breaks and avoid outdoor sports.", "priority": "medium"})
    if age_group == "Senior (60+)" and aqi > 100:
        actions.append({"text": "Contact your healthcare provider if any respiratory discomfort develops.", "priority": "medium"})
    if aqi > 100:
        actions.append({"text": "Stay well-hydrated — water helps your body manage pollutant exposure.", "priority": "low"})

    return actions


def generate_health_warning(
    aqi: int, pollutant: str, genetic_variants: list[str],
    age_group: str, conditions: list[str], activity: str,
) -> dict[str, Any]:
    genetic_data = get_genetic_sensitivity(genetic_variants)
    score = compute_personal_risk_score(aqi, pollutant, genetic_data, age_group, conditions, activity)
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "aqi": aqi,
        "pollutant": pollutant,
        "aqi_category": get_aqi_category(aqi),
        "genetic_data": genetic_data,
        "risk_score": score,
        "personal_risk": classify_personal_risk(score),
        "symptoms": get_symptoms_to_watch(pollutant, conditions),
        "actions": get_action_recommendations(score, aqi, activity, conditions, age_group),
    }


__all__ = [
    "get_aqi_category", "get_pollutant_multiplier", "get_genetic_sensitivity",
    "get_age_multiplier", "get_condition_bonus", "get_activity_multiplier",
    "compute_personal_risk_score", "classify_personal_risk", "get_symptoms_to_watch",
    "get_action_recommendations", "generate_health_warning", "show",
]


def show():
    st.markdown('<p class="section-title">🧬 Genetic & AQI Health Alerts</p>', unsafe_allow_html=True)
    st.markdown(
        "Personalized air-quality health warnings using your **genetic sensitivity profile** and "
        "**real-time AQI data** — zero AI API calls, pure logic."
    )

    st.divider()

    if "aqi_history" not in st.session_state:
        st.session_state.aqi_history = []

    col_form, col_bar = st.columns([2, 1], gap="large")

    with col_form:
        with st.form("genetic_aqi_form"):
            st.markdown("#### 🌫️ Air Quality Input")
            c1, c2 = st.columns(2)
            with c1:
                aqi = st.number_input("AQI value (0–500)", min_value=0, max_value=500, value=142, step=1)
            with c2:
                pollutant = st.selectbox("Main pollutant", ["PM2.5", "PM10", "Ozone (O₃)", "NO₂", "SO₂", "CO"])

            st.markdown("#### 🧬 Genetic Profile")
            genetic_variants = st.multiselect(
                "Known genetic variants (select all that apply)",
                [
                    "GSTP1 (oxidative stress sensitivity)",
                    "ADRB2 (bronchodilation response)",
                    "TNF-α (inflammatory response)",
                    "HLA-DRB1 (immune hypersensitivity)",
                    "NQO1 (detoxification deficiency)",
                    "ACE (cardiovascular sensitivity)",
                    "None / Unknown",
                ],
                default=["None / Unknown"],
                help="Select variants from your genomic report (23andMe, Ancestry, etc.)",
            )

            st.markdown("#### 👤 Health Profile")
            c3, c4 = st.columns(2)
            with c3:
                age_group = st.selectbox(
                    "Age group",
                    ["Child (under 12)", "Teen (12–17)", "Adult (18–60)", "Senior (60+)"],
                    index=2,
                )
            with c4:
                activity = st.selectbox(
                    "Planned outdoor activity",
                    ["No outdoor activity", "Light walk", "Moderate exercise", "Intense exercise"],
                )

            conditions = st.multiselect(
                "Pre-existing conditions",
                ["None", "Asthma", "COPD", "Heart disease", "Diabetes", "Pregnancy"],
                default=["None"],
            )

            submitted = st.form_submit_button("🔍 Generate Health Warning", use_container_width=True)

    with col_bar:
        st.markdown("#### 🌡️ AQI Scale")
        levels = [
            ("0–50", "Good", "#43a047"),
            ("51–100", "Moderate", "#fb8c00"),
            ("101–150", "Sensitive Groups", "#ef6c00"),
            ("151–200", "Unhealthy", "#e53935"),
            ("201–300", "Very Unhealthy", "#7b1fa2"),
            ("301–500", "Hazardous", "#bf360c"),
        ]
        for rng, label, color in levels:
            st.markdown(
                f"""<div style="display:flex;align-items:center;gap:10px;margin:5px 0">
                    <div style="width:14px;height:14px;border-radius:3px;background:{color};flex-shrink:0"></div>
                    <span style="font-size:0.82rem;color:#37474f"><b>{rng}</b> — {label}</span>
                </div>""",
                unsafe_allow_html=True,
            )

        st.divider()
        st.markdown("#### 🧬 Genetic Risk Factors")
        factor_info = {
            "GSTP1": "PM2.5 & Ozone", "ADRB2": "Ozone & NO₂", "TNF-α": "PM2.5, PM10 & SO₂",
            "HLA-DRB1": "NO₂ & SO₂", "NQO1": "PM2.5 & CO", "ACE": "PM2.5, CO & NO₂",
        }
        for gene, affects in factor_info.items():
            st.markdown(
                f"""<div style="margin:4px 0;font-size:0.82rem;color:#37474f">
                    <b style="color:#0f2027">{gene}</b> → {affects}</div>""",
                unsafe_allow_html=True,
            )

    if submitted:
        clean_conditions = [c for c in conditions if c != "None"] or ["None"]
        clean_variants = [v for v in genetic_variants if v != "None / Unknown"] or ["None / Unknown"]

        result = generate_health_warning(aqi, pollutant, clean_variants, age_group, clean_conditions, activity)

        st.session_state.aqi_history.insert(0, result)
        if len(st.session_state.aqi_history) > 10:
            st.session_state.aqi_history = st.session_state.aqi_history[:10]

        st.divider()
        st.markdown("### 📋 Your Personalized Health Warning")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("AQI Value", aqi)
        with m2:
            st.metric("AQI Category", result["aqi_category"]["label"].split()[0])
        with m3:
            st.metric("Risk Score", f"{result['risk_score']} / 10")
        with m4:
            st.metric("Genetic Sensitivity", result["genetic_data"]["level"].split()[0])

        p = result["personal_risk"]
        a = result["aqi_category"]
        st.markdown(
            f"""<div style="background:{p['bg']};border:2px solid {p['border']};
                border-radius:12px;padding:16px 20px;margin:12px 0;display:flex;
                align-items:center;gap:14px">
                <span style="font-size:2rem">{p['icon']}</span>
                <div>
                  <div style="font-size:1.2rem;font-weight:700;color:{p['color']}">{p['level']}</div>
                  <div style="font-size:0.88rem;color:#546e7a;margin-top:3px">
                    {a['emoji']} {a['label']} air quality · {result['genetic_data']['level']} ·
                    Assessed {result['timestamp']}
                  </div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown(f"**Personal risk score: {result['risk_score']} / 10**")
        st.progress(min(result["risk_score"] / 10.0, 1.0))

        st.divider()

        col_sym, col_act = st.columns(2, gap="large")

        with col_sym:
            st.markdown("#### 🩺 Symptoms to Watch For")
            if result["symptoms"]:
                for s in result["symptoms"]:
                    st.markdown(
                        f"""<div style="background:#f0f7ff;border-left:4px solid #1e88e5;
                            border-radius:0 8px 8px 0;padding:9px 14px;margin:5px 0;
                            font-size:0.9rem;color:#0f2027">• {s}</div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.success("No specific symptoms expected at this AQI level.")

        with col_act:
            st.markdown("#### ✅ Recommended Actions")
            priority_style = {
                "high": ("🔴", "#fff0f0", "#e53935"),
                "medium": ("🟡", "#fffbf0", "#fb8c00"),
                "low": ("🔵", "#f0f7ff", "#1e88e5"),
                "safe": ("🟢", "#f0faf0", "#43a047"),
            }
            for action in result["actions"]:
                icon, bg, border = priority_style.get(action["priority"], ("•", "#f5f5f5", "#ccc"))
                st.markdown(
                    f"""<div style="background:{bg};border-left:4px solid {border};
                        border-radius:0 8px 8px 0;padding:9px 14px;margin:5px 0;
                        font-size:0.9rem;color:#0f2027">{icon} {action['text']}</div>""",
                    unsafe_allow_html=True,
                )

        with st.expander("🧬 View genetic sensitivity breakdown"):
            st.markdown(f"**Overall:** {result['genetic_data']['level']}")
            st.markdown("Pollutant-specific sensitivity weights (1.0 = baseline):")
            wcols = st.columns(3)
            for i, (poll, weight) in enumerate(result["genetic_data"]["weights"].items()):
                color = "#e53935" if weight >= 1.5 else "#fb8c00" if weight >= 1.2 else "#43a047"
                with wcols[i % 3]:
                    st.markdown(
                        f"""<div style="background:white;border:1.5px solid #e0e7ef;
                            border-radius:10px;padding:12px;text-align:center;margin:4px 0">
                            <div style="font-size:0.8rem;color:#546e7a">{poll}</div>
                            <div style="font-size:1.3rem;font-weight:700;color:{color}">{weight}×</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

        with st.expander("⚙️ View logic breakdown (all def outputs)"):
            st.markdown("**`get_aqi_category(aqi)`**")
            st.json({k: v for k, v in result["aqi_category"].items() if k != "emoji"})

            st.markdown("**`get_pollutant_multiplier(pollutant)`**")
            st.write(get_pollutant_multiplier(pollutant))

            st.markdown("**`get_genetic_sensitivity(variants)`**")
            st.json(result["genetic_data"])

            st.markdown("**`get_age_multiplier(age_group)`**")
            st.write(get_age_multiplier(age_group))

            st.markdown("**`get_activity_multiplier(activity)`**")
            st.write(get_activity_multiplier(activity))

            st.markdown("**`get_condition_bonus(conditions)`**")
            st.write(get_condition_bonus(clean_conditions))

            st.markdown("**`compute_personal_risk_score(...)`**  → final score")
            st.write(result["risk_score"])

            st.markdown("**`classify_personal_risk(score)`**")
            st.json({k: v for k, v in result["personal_risk"].items() if k != "icon"})

            st.markdown("**`get_symptoms_to_watch(...)`**")
            st.write(result["symptoms"])

            st.markdown("**`get_action_recommendations(...)`**")
            for act in result["actions"]:
                st.write(f"[{act['priority'].upper()}] {act['text']}")

    if st.session_state.aqi_history:
        st.divider()
        st.markdown("### 📅 Recent Assessments")
        for entry in st.session_state.aqi_history:
            p = entry["personal_risk"]
            a = entry["aqi_category"]
            with st.expander(
                f"{p['icon']} {entry['timestamp']} — AQI {entry['aqi']} ({entry['pollutant']}) · {p['level']}"
            ):
                hc1, hc2, hc3 = st.columns(3)
                with hc1:
                    st.metric("AQI", entry["aqi"])
                with hc2:
                    st.metric("Risk Score", f"{entry['risk_score']} / 10")
                with hc3:
                    st.metric("Category", a["label"].split()[0])

                st.markdown("**Actions given:**")
                for act in entry["actions"][:3]:
                    st.write(f"• {act['text']}")

        if st.button("🗑️ Clear history"):
            st.session_state.aqi_history = []
            st.rerun()
