import streamlit as st
import re
RESPONSES = {
    r"(headache|head ache|head pain)": (
        "For headaches, try resting in a quiet dark room, stay hydrated, and consider OTC pain relief. "
        "If severe or recurring, consult a doctor."
    ),
    r"(fever|temperature|hot|38|39)": (
        "For fever, rest and drink plenty of fluids. Take paracetamol if needed. "
        "Seek medical help if temperature exceeds 39.5°C or persists beyond 3 days."
    ),
    r"(chest pain|chest tightness|heart)": (
        "⚠️ Chest pain can be serious. If you are experiencing severe chest pain, call emergency services immediately. "
        "Do not ignore chest pain especially if it radiates to arm or jaw."
    ),
    r"(cough|cold|flu|runny nose|sneezing)": (
        "For cold/cough symptoms: rest, stay warm, drink warm fluids with honey. "
        "If symptoms worsen or you have difficulty breathing, see a doctor."
    ),
    r"(diabetes|blood sugar|glucose|insulin)": (
        "Diabetes management involves monitoring blood sugar, following a low-glycaemic diet, regular exercise, "
        "and taking prescribed medication. Regular check-ups are essential."
    ),
    r"(blood pressure|hypertension|bp)": (
        "High blood pressure can be managed through low-sodium diet, regular exercise, stress reduction, "
        "and prescribed medication. Monitor BP regularly."
    ),
    r"(stress|anxiety|mental health|worried|anxious)": (
        "Stress and anxiety are common. Try deep breathing exercises, meditation, or a short walk. "
        "Talking to a mental health professional can be very helpful."
    ),
    r"(sleep|insomnia|can't sleep|tired)": (
        "For better sleep: maintain a consistent schedule, avoid screens before bed, limit caffeine after 2PM, "
        "and create a cool dark sleep environment."
    ),
    r"(diet|nutrition|food|eat|weight|obesity)": (
        "A balanced diet includes fruits, vegetables, whole grains, lean proteins, and healthy fats. "
        "Limit processed food, sugar, and salt. Consider consulting a nutritionist."
    ),
    r"(exercise|workout|gym|fitness|walk)": (
        "The WHO recommends 150 minutes of moderate exercise per week. "
        "Even a 30-minute daily walk can significantly improve health."
    ),
    r"(appointment|doctor|hospital|consult)": (
        "You can use the Doctor Panel to request a clinical review. "
        "For emergencies, please contact your nearest hospital immediately."
    ),
    r"(hello|hi|hey|good morning|good evening)": (
        "Hello! I'm your NLP-Medora Health Assistant. How can I help you today? "
        "You can ask me about symptoms, medications, diet, or general health advice."
    ),
    r"(thank|thanks|thank you)": (
        "You're welcome! Stay healthy and take care. Remember — I'm here whenever you have health questions! 😊"
    ),
    r"(covid|coronavirus|pandemic|vaccine|vaccination)": (
        "COVID-19 vaccines are safe and effective. Symptoms include fever, cough, and fatigue. "
        "If experiencing severe symptoms, seek medical attention promptly."
    ),
}
POSITIVE_WORDS = {"good", "great", "better", "fine", "happy", "healthy", "well", "excellent", "wonderful"}
NEGATIVE_WORDS = {"bad", "terrible", "sick", "pain", "hurt", "awful", "worst", "suffering", "ill", "weak", "tired", "worried"}

def detect_sentiment(text):
    words = set(text.lower().split())
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    if neg > pos:
        return "😔 Concerned", "alert-amber"
    elif pos > neg:
        return "😊 Positive", "alert-green"
    else:
        return "😐 Neutral", "alert-blue"

def get_response(user_input):
    user_lower = user_input.lower()
    for pattern, response in RESPONSES.items():
        if re.search(pattern, user_lower):
            return response
    return(
        "I'm not sure about that specific query. For the best advice, please consult a qualified healthcare professional. "
        "You can also try our Symptom Checker or browse the Symptom Database for more information."
    )

def show():
    st.markdown('<p class="section-title">🤖 Health Chatbot Assistant</p>', unsafe_allow_html=True)
    st.caption("Ask general health questions — I'll give rule-based medical guidance.")

    # ── Sentiment status ────────────────────────────────────────────────────────
    if st.session_state.chat_history:
        last_user = [m["content"] for m in st.session_state.chat_history if m["role"] == "user"]
        if last_user:
            sentiment, color = detect_sentiment(last_user[-1])
            st.markdown(f'<div class="{color}">🧠 <b>Emotional Tone Detected:</b> {sentiment}</div>', unsafe_allow_html=True)

    st.divider()

    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="chat-bot">
            👋 Hello! I'm your NLP-Medora Health Assistant.<br>
            Ask me about symptoms, medications, diet, sleep, stress, or general health tips!
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("**💡 Quick Questions:**")
    q_cols = st.columns(4)
    quick = ["I have a headache", "I feel anxious", "Tips for better sleep", "I have chest pain"]
    for i, q in enumerate(quick):
        if q_cols[i].button(q, key=f"q_{i}"):
            response = get_response(q)
            st.session_state.chat_history.append({"role": "user", "content": q})
            st.session_state.chat_history.append({"role": "bot", "content": response})
            st.rerun()

    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([5, 1])
        user_msg = c1.text_input("Type your health question...", label_visibility="collapsed", placeholder="e.g. I have been feeling tired lately...")
        send = c2.form_submit_button("Send ➤")

    if send and user_msg.strip():
        response = get_response(user_msg)
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        st.session_state.chat_history.append({"role": "bot", "content": response})
        st.rerun()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

