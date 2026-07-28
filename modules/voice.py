import streamlit as st
from services.speech_service import transcribe_audio
from services.soap_service import generate_soap
from services.nlp_utils import detect_risk


def show():
    st.title("🎙️ Voice-to-Text Medical System")

    tab1, tab2 = st.tabs(["🎤 Upload Audio", "📋 SOAP Generator"])

    with tab1:
        audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3"])

        if audio_file:
            ext = audio_file.name.split(".")[-1].lower()
            st.audio(audio_file.getvalue(), format=f"audio/{ext}")
            st.caption(f"Loaded file: {audio_file.name} ({ext.upper()})")

            if st.button("Transcribe"):
                with st.spinner("Processing..."):
                    text = transcribe_audio(audio_file)

                st.text_area("Transcript", text, height=150)
                st.session_state["transcript"] = text

                risk = detect_risk(text)
                st.info(f"🧠 Risk Detection: {risk}")

    with tab2:
        text = st.text_area("Enter Transcript")

        if st.button("Generate SOAP"):
            if text:
                soap = generate_soap(text)
                st.text_area("SOAP Note", soap, height=300)

                st.download_button(
                    "Download",
                    data=soap,
                    file_name="soap.txt"
                )