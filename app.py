import streamlit as st
from modules.db import seed_demo_users_if_empty, get_unread_message_count, get_upcoming_appointment_count

st.set_page_config(
    page_title="NLP-Medora | AI Health Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Shared session state ──────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "users_db" not in st.session_state:
    st.session_state.users_db = seed_demo_users_if_empty()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "health_logs" not in st.session_state:
    st.session_state.health_logs = []
if "prediction_requests" not in st.session_state:
    st.session_state.prediction_requests = []
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
 
    /* ── Base & Background ── */
    html, body { font-family: 'Inter', 'Segoe UI', sans-serif; }
 
    .stApp {
        background: linear-gradient(135deg, #e8f4f8 0%, #f0f7ff 50%, #e8f0fe 100%) !important;
        min-height: 100vh;
    }
 
    .main .block-container {
        background: transparent !important;
        padding: 2rem 2.5rem 2rem 2.5rem !important;
        max-width: 1200px;
    }
 
    /* ── Headings & Body ── */
    h1, h2, h3, h4, h5 {
        color: #0f2027 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    p, li {
        color: #37474f;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
 
    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
    }
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    /* Only colour sidebar-native text, not everything */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] .stCaption {
        color: #e8f4f8 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(8, 20, 28, 0.72) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        color: #f6fbff !important;
        border-radius: 10px !important;
        width: 100% !important;
        margin-bottom: 5px !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
        padding: 0.5rem 1rem !important;
    }
    section[data-testid="stSidebar"] .stButton > button,
    section[data-testid="stSidebar"] .stButton > button p,
    section[data-testid="stSidebar"] .stButton > button span {
        color: #f6fbff !important;
        -webkit-text-fill-color: #f6fbff !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(12, 30, 40, 0.92) !important;
        border-color: rgba(255,255,255,0.6) !important;
        transform: translateX(3px) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2) !important;
    }
 
    /* Sidebar form fields — light bg so text is readable on dark sidebar */
    section[data-testid="stSidebar"] .stTextInput > div > div > input,
    section[data-testid="stSidebar"] .stNumberInput > div > div > input,
    section[data-testid="stSidebar"] .stTextArea > div > div > textarea,
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stMultiSelect > div > div {
        background: #eef3f7 !important;
        border: 1.5px solid #b0bec5 !important;
        color: #0f2027 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input::placeholder,
    section[data-testid="stSidebar"] .stNumberInput input::placeholder,
    section[data-testid="stSidebar"] .stTextArea textarea::placeholder {
        color: #546e7a !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stNumberInput input,
    section[data-testid="stSidebar"] .stTextArea textarea,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] *,
    section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] * {
        color: #0f2027 !important;
    }
 
    /* ── Metric Cards ── */
    div[data-testid="stMetric"] {
        background: white !important;
        border-radius: 14px !important;
        padding: 18px 20px !important;
        box-shadow: 0 4px 15px rgba(44,83,100,0.12) !important;
        border-left: 4px solid #2c5364 !important;
        border-top: 1px solid rgba(44,83,100,0.08) !important;
    }
    div[data-testid="stMetric"] label {
        color: #546e7a !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f2027 !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #37474f !important;
    }
 
    /* ── Input Fields ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: white !important;
        border: 1.5px solid #cfd8dc !important;
        border-radius: 10px !important;
        color: #0f2027 !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.2s !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    .stNumberInput input::placeholder {
        color: #90a4ae !important;
        opacity: 1 !important;
    }
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] *,
    .stMultiSelect div[data-baseweb="select"] * {
        color: #0f2027 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #2c5364 !important;
        box-shadow: 0 0 0 3px rgba(44,83,100,0.1) !important;
    }
    .stTextInput label, .stTextArea label,
    .stSelectbox label, .stNumberInput label,
    .stSlider label, .stRadio label,
    .stCheckbox label, .stMultiSelect label {
        color: #37474f !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
 
    /* ── Buttons (main area) ── */
    .stButton > button {
        background: linear-gradient(135deg, #2c5364, #203a43) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 3px 10px rgba(44,83,100,0.3) !important;
    }
    .stButton > button,
    .stButton > button p,
    .stButton > button span,
    .stButton > button div,
    .stForm button,
    .stForm button p,
    .stForm button span,
    button[kind="primary"],
    button[kind="primary"] p,
    button[kind="secondary"],
    button[kind="secondary"] p {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #37626f, #2c5364) !important;
        box-shadow: 0 5px 15px rgba(44,83,100,0.4) !important;
        transform: translateY(-1px) !important;
    }
    button[kind="secondary"],
    [data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #455a64, #37474f) !important;
        border: 1px solid #2f3c42 !important;
    }
 
    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: white !important;
        border-radius: 12px !important;
        padding: 4px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        gap: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 10px !important;
        color: #546e7a !important;
        font-weight: 500 !important;
        padding: 8px 20px !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2c5364, #203a43) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span {
        color: white !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        padding-top: 1rem !important;
    }
    /* Tab panel: only colour base text, let child components keep their own colours */
    .stTabs [data-baseweb="tab-panel"] > div > p,
    .stTabs [data-baseweb="tab-panel"] > div > li {
        color: #37474f !important;
    }
 
    /* ── Expanders ── */
    [data-testid="stExpander"] {
        background: white !important;
        border-radius: 12px !important;
        border: 1.5px solid #e0e7ef !important;
        margin-bottom: 8px !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"]:hover {
        border-color: #2c5364 !important;
    }
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 12px 12px 0 0 !important;
        color: #0f2027 !important;
        font-weight: 600 !important;
        padding: 14px 18px !important;
    }
    .streamlit-expanderHeader:hover {
        background: #f0f7ff !important;
    }
    .streamlit-expanderHeader p {
        margin: 0 !important;
        color: #0f2027 !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderContent {
        background: white !important;
        border-top: 1.5px solid #e0e7ef !important;
        padding: 16px 18px !important;
        color: #37474f !important;
    }
    [data-testid="stExpanderDetails"] {
        background: white !important;
        border-top: 1.5px solid #e0e7ef !important;
        padding: 16px 18px !important;
    }
 
    /* ── Selectbox / Dropdown ── */
    .stSelectbox [data-baseweb="select"] > div {
        background: white !important;
        border: 1.5px solid #cfd8dc !important;
        border-radius: 10px !important;
        color: #0f2027 !important;
    }
 
    /* ── Multiselect ── */
    .stMultiSelect [data-baseweb="select"] > div {
        background: white !important;
        border: 1.5px solid #cfd8dc !important;
        border-radius: 10px !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        background: #2c5364 !important;
        color: white !important;
        border-radius: 6px !important;
    }
 
    /* ── Checkboxes ── */
    .stCheckbox > label {
        background: white !important;
        border: 1.5px solid #e0e7ef !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        width: 100% !important;
        transition: all 0.15s !important;
        color: #37474f !important;
    }
    .stCheckbox > label:hover {
        border-color: #2c5364 !important;
        background: #f0f7ff !important;
    }
 
    /* ── Dataframes ── */
    .stDataFrame {
        background: white !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06) !important;
    }
 
    /* ── Forms ── */
    [data-testid="stForm"] {
        background: white !important;
        border: 1.5px solid #e0e7ef !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 2px 12px rgba(44,83,100,0.08) !important;
    }
 
    /* ── Divider ── */
    hr {
        border: none !important;
        border-top: 1.5px solid #e0e7ef !important;
        margin: 1.2rem 0 !important;
    }
 
    /* ── Section Title ── */
    .section-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f2027;
        margin-bottom: 0.3rem;
        padding-bottom: 8px;
        border-bottom: 3px solid #2c5364;
        display: inline-block;
    }
 
    /* ── Cards ── */
    .card {
        background: white;
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 3px 14px rgba(44,83,100,0.1);
        margin-bottom: 14px;
        border: 1px solid rgba(44,83,100,0.07);
        transition: box-shadow 0.2s;
        color: #0f2027;
    }
    .card p, .card li, .card span, .card b, .card strong {
        color: #37474f;
    }
    .card:hover {
        box-shadow: 0 6px 20px rgba(44,83,100,0.15);
    }
 
    /* ── Alert Boxes ── */
    .alert-red {
        background: #fff0f0;
        border-left: 5px solid #e53935;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 8px 0;
        color: #7f1c1c;
    }
    .alert-red p, .alert-red span, .alert-red li { color: #7f1c1c !important; }
 
    .alert-green {
        background: #e8f5e9;
        border-left: 5px solid #2e7d32;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 8px 0;
        color: #1b5e20;
    }
    .alert-green p, .alert-green span, .alert-green li { color: #1b5e20 !important; }
 
    .alert-blue {
        background: #e3f2fd;
        border-left: 5px solid #1565c0;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 8px 0;
        color: #0d3c78;
    }
    .alert-blue p, .alert-blue span, .alert-blue li { color: #0d3c78 !important; }
 
    .alert-amber {
        background: #fff8e1;
        border-left: 5px solid #f57f17;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 8px 0;
        color: #7a4400;
    }
    .alert-amber p, .alert-amber span, .alert-amber li { color: #7a4400 !important; }
 
    /* ── Chat Bubbles ── */
    .chat-user {
        background: linear-gradient(135deg, #2c5364, #203a43);
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 72%;
        margin-left: auto;
        box-shadow: 0 2px 8px rgba(44,83,100,0.25);
        font-size: 0.92rem;
    }
    /* User bubble: white text on dark background */
    .chat-user,
    .chat-user p,
    .chat-user span {
        color: #ffffff !important;
    }
 
    .chat-bot {
        background: white;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 72%;
        border: 1.5px solid #e0e7ef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        font-size: 0.92rem;
    }
    /* Bot bubble: dark text on white background */
    .chat-bot,
    .chat-bot p,
    .chat-bot span {
        color: #0f2027 !important;
    }
 
    /* ── SOAP Note ── */
    .soap {
        background: #f8faff;
        border: 1.5px solid #c5cae9;
        border-radius: 12px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        font-size: 0.87rem;
        line-height: 1.7;
        color: #1a237e !important;
    }
    .soap p, .soap span, .soap li { color: #1a237e !important; }
 
    /* ── Radio buttons ── */
    .stRadio > div {
        background: white !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1.5px solid #e0e7ef !important;
    }
    .stRadio > div label { color: #37474f !important; }
 
    /* ── Slider ── */
    .stSlider > div > div > div {
        background: #2c5364 !important;
    }
 
    /* ── Success / Warning / Error / Info messages ── */
    div[data-testid="stSuccess"],
    div[data-testid="stSuccess"] p { 
        background: #e8f5e9 !important;
        border: 1.5px solid #2e7d32 !important;
        border-radius: 10px !important;
        color: #1b5e20 !important;
    }
    div[data-testid="stWarning"],
    div[data-testid="stWarning"] p {
        background: #fff8e1 !important;
        border: 1.5px solid #f57f17 !important;
        border-radius: 10px !important;
        color: #7a4400 !important;
    }
    div[data-testid="stError"],
    div[data-testid="stError"] p {
        background: #fff0f0 !important;
        border: 1.5px solid #e53935 !important;
        border-radius: 10px !important;
        color: #7f1c1c !important;
    }
    div[data-testid="stInfo"],
    div[data-testid="stInfo"] p {
        background: #e3f2fd !important;
        border: 1.5px solid #1565c0 !important;
        border-radius: 10px !important;
        color: #0d3c78 !important;
    }
 
    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: white !important;
        border: 2px dashed #2c5364 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span { color: #37474f !important; }
 
    /* ── Download button ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e88e5, #1565c0) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    .stDownloadButton > button,
    .stDownloadButton > button p,
    .stDownloadButton > button span {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
 
    /* ── Caption ── */
    .stCaption, small {
        color: #78909c !important;
        font-size: 0.82rem !important;
    }
 
    /* ── Material Icons ── */
    span.material-icons,
    span.material-icons-round,
    span.material-icons-outlined,
    span.material-symbols-rounded,
    span.material-symbols-outlined {
        font-family: "Material Icons", "Material Symbols Rounded", "Material Symbols Outlined" !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
    }
 
    /* ── Hide Streamlit defaults ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────────────────────────
def sidebar_nav():
    with st.sidebar:
        st.markdown("## 🏥 NLP-Medora")
        st.markdown("*AI Health Management*")
        st.divider()

        if not st.session_state.logged_in:
            st.markdown("### 🔐 Access")
            if st.button("Login / Register"):
                st.session_state.current_page = "auth"
        else:
            # ── User info ──────────────────────────────────────────
            role_icon = {"User":"👤","Doctor":"🩺","Admin":"⚙️"}.get(st.session_state.user_role,"👤")
            st.markdown(f"{role_icon} **{st.session_state.username}**")
            st.markdown(f"`{st.session_state.user_role}`")

            # ── Pending badges ─────────────────────────────────────
            reqs = st.session_state.get("prediction_requests", [])

            if st.session_state.user_role in ("Doctor", "User"):
                unread_msgs = get_unread_message_count(st.session_state.get("user_email", ""))
                if unread_msgs:
                    st.markdown(f"""<div style="background:#25d366;color:white;border-radius:8px;
                        padding:6px 12px;font-size:0.85rem;font-weight:600;margin:4px 0;">
                        💬 {unread_msgs} new message(s)</div>""", unsafe_allow_html=True)

                upcoming_appts = get_upcoming_appointment_count(
                    st.session_state.get("user_email", ""), st.session_state.user_role
                )
                if upcoming_appts:
                    st.markdown(f"""<div style="background:#1e88e5;color:white;border-radius:8px;
                        padding:6px 12px;font-size:0.85rem;font-weight:600;margin:4px 0;">
                        📅 {upcoming_appts} upcoming appointment(s)</div>""", unsafe_allow_html=True)

            if st.session_state.user_role == "Doctor":
                my_email = st.session_state.get("user_email", "")
                pending = len([
                    r for r in reqs
                    if r["status"] == "Pending"
                    and (
                        r.get("assigned_doctor_email") == my_email
                        or (not r.get("assigned_doctor_email") and not r.get("assigned_doctor"))
                    )
                ])
                if pending:
                    st.markdown(f"""<div style="background:#e53935;color:white;border-radius:8px;
                        padding:6px 12px;font-size:0.85rem;font-weight:600;margin:4px 0;">
                        🔴 {pending} review(s) waiting</div>""", unsafe_allow_html=True)
            
            elif st.session_state.user_role == "User":
                my_email = st.session_state.get("user_email","")
                my_done  = len([r for r in reqs if r["patient_email"]==my_email and r["status"] in ["Verified","Rejected"]])
                if my_done:
                    st.markdown(f"""<div style="background:#1e88e5;color:white;border-radius:8px;
                        padding:6px 12px;font-size:0.85rem;font-weight:600;margin:4px 0;">
                        ✅ {my_done} doctor response(s) ready</div>""", unsafe_allow_html=True)
            
            elif st.session_state.user_role == "Admin":
                db = st.session_state.users_db
                unverified = len([e for e,u in db.items() if u["role"]=="Doctor" and not u.get("verified")])
                if unverified:
                    st.markdown(f"""<div style="background:#fb8c00;color:white;border-radius:8px;
                        padding:6px 12px;font-size:0.85rem;font-weight:600;margin:4px 0;">
                        ⚠️ {unverified} doctor(s) need verification</div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("### 📋 Navigation")

            pages_all = {
                "🏠 Dashboard":             "dashboard",
                "💬 Messages":              "messages",
                "📅 Appointments":          "appointments",
                "💊 Symptom Checker":       "symptoms",
                "🤖 Health Chatbot":        "chatbot",
                "🎙️ Voice-to-Text":         "voice",
                "📄 Report Simplifier":     "reports",
                "🧬 Genetic":               "genetic",
                "🥗 Smart Nutrition":       "nutrition",
                "📊 Health vs Wealth":      "visualization",
                "🔬 AI Predictions":        "predictions",
                "📩 Doctor Notes":          "patient_notes",                 
                "👤 My Profile":            "profile",
                "🌤️ AQI":                   "AQI",
                "🏃‍♂️ Life Style Predictor":  "life_Style_Predictor",
                "⚖️ BMI Calculator":        "BMIFront"
            }
            pages_doctor = {
                "🩺 Doctor Panel":          "doctor",
            }
            pages_admin = {
                "⚙️ Admin Panel":           "admin",
            }

            for label, page in pages_all.items():
                if st.button(label):
                    st.session_state.current_page = page

            if st.session_state.user_role == "Doctor":
                st.divider()
                for label, page in pages_doctor.items():
                    if st.button(label):
                        st.session_state.current_page = page

            if st.session_state.user_role == "Admin":
                st.divider()
                for label, page in pages_admin.items():
                    if st.button(label):
                        st.session_state.current_page = page

            st.divider()
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.user_role = None
                st.session_state.username = ""
                st.session_state.user_email = ""
                st.session_state.current_page = "auth"
                st.rerun()

# ── Page routing ──────────────────────────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state.current_page = "auth"

sidebar_nav()

page = st.session_state.current_page

if page == "auth":
    from modules.auth import show
    show()
elif not st.session_state.logged_in:
    st.warning("⚠️ Please log in to access the dashboard.")
    from modules.auth import show
    show()
else:
    if page == "dashboard":
        from modules.dashboard import show
        show()
    elif page == "messages":
        from modules.messages import show
        show()
    elif page == "appointments":
        from modules.appointments import show
        show()
    elif page == "symptoms":
        from modules.symptoms import show
        show()
    elif page == "chatbot":
        from modules.chatbot import show
        show()
    elif page == "voice":
        from modules.voice import show
        show()
    elif page == "reports":
        from modules.reports import show
        show()
    elif page == "genetic":
        from modules.genetic import show
        show()
    elif page == "nutrition":
        from modules.nutrition import show
        show()
    elif page == "visualization":
        from modules.visualization import show
        show()
    elif page == "predictions":
        from modules.predictions import show
        show()
    elif page == "profile":
        from modules.profile import show
        show()
    elif page == "doctor":
        from modules.doctor import show
        show()
    elif page == "admin":
        from modules.admin import show
        show()

    elif page == "patient_notes":
        from modules.patient_notes import show
        show()
    elif page == "AQI":
        from modules.AQI import show
        show()
    elif page=="life_Style_Predictor":
        from modules.life_Pred import show
        show()
    elif page=="BMIFront":
        from modules.BMIFront import show
        show()
    else:
        from modules.dashboard import show
        show()
