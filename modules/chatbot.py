import re
import streamlit as st

from services import rag_engine
from services.nlp_utils import detect_risk

# ─────────────────────────────────────────────────────────────────────────────
#  Sentiment / emotion helpers (kept — cheap, useful context shown alongside
#  the RAG-generated answer; these do NOT generate the answer itself anymore)
# ─────────────────────────────────────────────────────────────────────────────
POSITIVE_WORDS = {
    "good", "great", "better", "fine", "happy", "healthy", "well",
    "excellent", "wonderful", "recovering", "improving", "recovered", "okay"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "sick", "pain", "hurt", "awful", "worst", "suffering",
    "ill", "weak", "tired", "worried", "depressed", "anxious", "scared",
    "dying", "bleeding", "swollen", "burning", "nauseous", "dizzy", "severe"
}

EMOTION_PATTERNS = {
    "Stress": [
        r"\bstress(ed|ful)?\b",
        r"\boverwhelmed\b",
        r"\bburnout\b",
        r"\btoo much pressure\b",
        r"\bcan'?t cope\b",
    ],
    "Anxiety": [
        r"\banxious\b",
        r"\banxiety\b",
        r"\bpanic\b",
        r"\bpanic attack\b",
        r"\bnervous\b",
        r"\bworry(ing)?\b",
        r"\bracing thoughts?\b",
    ],
    "Depressive mood": [
        r"\bdepress(ed|ion)?\b",
        r"\bhopeless\b",
        r"\bempty\b",
        r"\bno motivation\b",
        r"\bworthless\b",
        r"\bsad all the time\b",
    ],
}


def detect_sentiment(text: str) -> tuple[str, str]:
    words = set(text.lower().split())
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    if neg > pos:
        return "😔 Concerned", "alert-amber"
    elif pos > neg:
        return "😊 Positive", "alert-green"
    return "😐 Neutral", "alert-blue"


def detect_emotional_state(text: str) -> str:
    user_lower = text.lower()
    for state, patterns in EMOTION_PATTERNS.items():
        if any(re.search(pattern, user_lower) for pattern in patterns):
            return state
    return "No clear emotional distress detected"


# ─────────────────────────────────────────────────────────────────────────────
#  Rendering helpers
# ─────────────────────────────────────────────────────────────────────────────
def _render_disease_card(pred) -> None:
    if not pred:
        return
    symptoms_str = ", ".join(s.replace("_", " ") for s in pred.matched_symptoms)
    icon = (pred.info or {}).get("icon", "🩺")
    urgency = (pred.info or {}).get("urgency", "Unknown")
    st.info(
        f"{icon} **Symptom-model check** — matched symptoms: *{symptoms_str}*\n\n"
        f"Closest match: **{pred.disease}** ({pred.confidence}% confidence) · Urgency: **{urgency}**\n\n"
        f"_This is a pattern match from a trained model, not a diagnosis._"
    )
    if pred.alternatives:
        alt_str = ", ".join(f"{a['disease']} ({a['confidence']}%)" for a in pred.alternatives)
        st.caption(f"Other possibilities considered: {alt_str}")


def _render_sources(sources) -> None:
    if not sources:
        return
    with st.expander(f"🔎 Sources used ({len(sources)})"):
        for i, doc in enumerate(sources, start=1):
            snippet = doc.answer[:350].rstrip()
            if len(doc.answer) > 350:
                snippet += "…"
            st.markdown(
                f"**{i}. {doc.question}**  \n_relevance: {doc.score:.2f} · source: `{doc.source}`_\n\n{snippet}"
            )
            if i < len(sources):
                st.divider()


def _render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            _render_disease_card(message.get("disease_prediction"))
            _render_sources(message.get("sources"))
            if message.get("llm_error"):
                st.caption(
                    f"⚠️ Couldn't reach Ollama ({message['llm_error']}) — showing retrieved "
                    f"reference information directly instead of an LLM-generated answer."
                )


# ─────────────────────────────────────────────────────────────────────────────
#  Main Streamlit page
# ─────────────────────────────────────────────────────────────────────────────
def show():
    st.header("💬 Medora AI Chatbot (RAG-powered)")
    st.write(
        "Ask me health-related questions. Answers are grounded in our medical knowledge base "
        "and, if relevant, cross-checked against a symptom-based prediction model."
    )

    # ── Sidebar / settings ───────────────────────────────────────────────────
    with st.sidebar:
        st.subheader("⚙️ RAG Settings")
        ollama_host = st.text_input("Ollama host", value=rag_engine.OLLAMA_HOST)
        available_models = rag_engine.list_ollama_models(ollama_host)
        if available_models:
            default_idx = (
                available_models.index(rag_engine.DEFAULT_OLLAMA_MODEL)
                if rag_engine.DEFAULT_OLLAMA_MODEL in available_models
                else 0
            )
            ollama_model = st.selectbox("Ollama model", available_models, index=default_idx)
        else:
            ollama_model = st.text_input("Ollama model (not auto-detected)", value=rag_engine.DEFAULT_OLLAMA_MODEL)

        connected = rag_engine.ollama_is_available(ollama_host)
        if connected:
            st.success("Ollama: connected ✅")
        else:
            st.warning("Ollama: not reachable — will fall back to retrieval-only answers.")

        top_k = st.slider("Chunks to retrieve", min_value=1, max_value=8, value=4)
        use_llm = st.checkbox("Generate with LLM (uncheck for retrieval-only)", value=True)

        if st.button("🔄 Rebuild knowledge index"):
            with st.spinner("Rebuilding TF-IDF index from data files..."):
                rag_engine.build_index(force=True)
            st.success("Index rebuilt.")

    # ── Chat state ───────────────────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        _render_message(message)

    # ── Handle new input ─────────────────────────────────────────────────────
    if prompt := st.chat_input("Type your health query here..."):
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        with st.chat_message("user"):
            st.markdown(prompt)

        sentiment, _ = detect_sentiment(prompt)
        emotional_state = detect_emotional_state(prompt)
        risk_level = detect_risk(prompt)

        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]

        with st.chat_message("assistant"):
            with st.spinner("Retrieving relevant knowledge and generating an answer..."):
                result = rag_engine.answer(
                    prompt,
                    chat_history=history,
                    top_k=top_k,
                    ollama_model=ollama_model,
                    ollama_host=ollama_host,
                    use_llm=use_llm,
                )

            status_line = (
                f"**Status:** {sentiment} &nbsp;|&nbsp; "
                f"**Emotional state:** {emotional_state} &nbsp;|&nbsp; "
                f"**Risk:** {risk_level}"
            )
            st.markdown(status_line)
            st.markdown(result.answer)
            _render_disease_card(result.disease_prediction)
            _render_sources(result.sources)
            if result.llm_error:
                st.caption(
                    f"⚠️ Couldn't reach Ollama ({result.llm_error}) — showing retrieved "
                    f"reference information directly instead of an LLM-generated answer."
                )

        assistant_message = {
            "role": "assistant",
            "content": f"{status_line}\n\n{result.answer}",
            "sources": result.sources,
            "disease_prediction": result.disease_prediction,
            "llm_error": result.llm_error,
        }
        st.session_state.messages.append(assistant_message)
