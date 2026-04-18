import streamlit as st
import json

def show():
    st.markdown('<p class="section-title">🎙️ Voice-to-Text Medical Input</p>', unsafe_allow_html=True)
    st.markdown("Upload audio files to convert spoken health notes into editable clinical text.")

    st.markdown("""
    <div class="alert-blue">
    <b>ℹ️ How it works:</b> Upload an audio file (WAV, MP3, M4A, OGG) containing medical dictation. 
    This is a frontend prototype - transcription is simulated for demonstration purposes.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    tab1, tab2 = st.tabs(["🎤 Upload Audio File", "📋 Text-to-SOAP Note Generator"])

    with tab1:
        st.markdown("### Upload Audio for Transcription")
        st.caption("Supported formats: WAV, MP3, M4A, OGG (Max size: 200MB)")
        
        # File uploader
        audio_file = st.file_uploader(
            "Choose an audio file",
            type=["wav", "mp3", "m4a", "ogg"],
            help="Upload an audio file for simulated transcription"
        )
        
        # Language selection
        source_language = st.selectbox(
            "Original Language of Recording",
            ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Hindi", "Chinese", "Japanese", "Arabic"],
            help="Select the language spoken in the audio (simulated)"
        )
        
        if audio_file is not None:
            # Display audio player
            st.audio(audio_file, format=f"audio/{audio_file.type.split('/')[-1]}")
            
            # Simulate transcription button
            if st.button("🎙️ Simulate Transcription", type="primary"):
                with st.spinner("Simulating transcription process..."):
                    # Simulated transcription based on language selection
                    simulated_transcripts = {
                        "English": "Patient reports intermittent chest tightness for the last 3 days. Pain worsens on exertion. No fever. Blood pressure was noted as elevated at 145 over 92. Patient is 52 years old, male, smoker.",
                        "Spanish": "El paciente reporta opresión en el pecho intermitente durante los últimos 3 días. El dolor empeora con el esfuerzo. Sin fiebre. La presión arterial se observó elevada en 145 sobre 92. El paciente tiene 52 años, hombre, fumador.",
                        "French": "Le patient signale une oppression thoracique intermittente depuis 3 jours. La douleur s'aggrave à l'effort. Pas de fièvre. La tension artérielle était élevée à 145 sur 92. Le patient est un homme de 52 ans, fumeur.",
                        "German": "Patient berichtet über intermittierendes Engegefühl in der Brust seit 3 Tagen. Schmerzen verschlimmern sich bei Belastung. Kein Fieber. Blutdruck war erhöht mit 145 zu 92. Patient ist 52 Jahre alt, männlich, Raucher.",
                        "Italian": "Il paziente riferisce oppressione toracica intermittente negli ultimi 3 giorni. Il dolore peggiora con lo sforzo. Nessuna febbre. La pressione sanguigna era elevata a 145 su 92. Paziente di 52 anni, maschio, fumatore.",
                        "Portuguese": "Paciente relata aperto no peito intermitente nos últimos 3 dias. A dor piora com esforço. Sem febre. Pressão arterial elevada em 145 por 92. Paciente tem 52 anos, homem, fumante.",
                        "Hindi": "मरीज पिछले 3 दिनों से रुक-रुक कर सीने में जकड़न की रिपोर्ट करता है। परिश्रम पर दर्द बढ़ जाता है। बुखार नहीं। रक्तचाप 145/92 दर्ज किया गया। मरीज 52 वर्ष का पुरुष, धूम्रपान करने वाला है।",
                        "Chinese": "患者报告过去3天间歇性胸闷。劳累时疼痛加重。无发热。血压升高至145/92。患者52岁，男性，吸烟者。",
                        "Japanese": "患者は過去3日間の断続的な胸の圧迫感を報告。労作で痛みが悪化。発熱なし。血圧は145/92と上昇。患者は52歳の男性喫煙者。",
                        "Arabic": "يبلغ المريض عن ضيق متقطع في الصدر خلال الأيام الثلاثة الماضية. يزداد الألم مع المجهود. لا حمى. لوحظ ارتفاع ضغط الدم عند 145/92. المريض يبلغ من العمر 52 عامًا، ذكر، مدخن."
                    }
                    
                    original_text = simulated_transcripts.get(source_language, simulated_transcripts["English"])
                    
                    if source_language != "English":
                        st.success(f"✅ Transcription simulation complete! Original language: {source_language}")
                        
                        # Display both original and translated text
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 📝 Original Transcript")
                            st.text_area("Original:", original_text, height=150, key="original")
                        with col2:
                            st.markdown("#### 🌐 English Translation")
                            # Simulated English translation
                            english_translation = simulated_transcripts["English"]
                            final_text = st.text_area("Translated:", english_translation, height=150, key="translated")
                    else:
                        st.markdown("#### 📝 Transcribed Text")
                        final_text = st.text_area("Edit transcription:", original_text, height=150, key="transcribed")
                    
                    # Store in session state
                    st.session_state["voice_transcript"] = final_text
                    
                    # Generate SOAP button
                    if st.button("▶️ Generate SOAP Note from this transcript", type="secondary"):
                        st.session_state["soap_ready"] = True
                        st.rerun()
        
        # Manual text input option
        st.markdown("---")
        st.markdown("### Or type your transcript manually")
        manual_text = st.text_area("✏️ Type/paste voice transcript here:", height=120,
                                    placeholder="e.g. Patient complains of severe headache for 2 days...")
        
        if manual_text:
            if st.button("▶️ Generate SOAP Note from typed text"):
                st.session_state["voice_transcript"] = manual_text
                st.session_state["soap_ready"] = True
                st.rerun()
        with tab2:
        st.markdown("### 📋 SOAP Note Generator")
        st.caption("Converts clinical text into a structured SOAP note.")

        if "soap_ready" in st.session_state and st.session_state.soap_ready:
            transcript = st.session_state.get("voice_transcript", "")
        else:
            transcript = st.text_area("Paste clinical transcript:", height=130,
                                       placeholder="Patient is a 60-year-old male reporting shortness of breath...",
                                       key="soap_input")

        if st.button("🧠 Generate SOAP Note", key="gen_soap") or st.session_state.get("soap_ready"):
            if transcript:
                st.session_state["soap_ready"] = False
                soap = generate_soap(transcript)
                st.markdown("#### 🗒️ Generated SOAP Note")
                st.markdown(f'<div class="soap">{soap}</div>', unsafe_allow_html=True)
                st.download_button("⬇️ Download SOAP Note (.txt)", data=soap.replace("<br>","").replace("<b>","").replace("</b>",""),
                                   file_name="soap_note.txt", mime="text/plain")
            else:
                st.warning("Please enter a transcript first.")
    
def generate_soap(text):
    """Simple SOAP note generator using keyword extraction."""
    import re
    from datetime import datetime
    
    text_lower = text.lower()

    # Extract age/gender
    age_match = re.search(r'(\d+)[- ]year[s]?[- ]old', text_lower)
    gender_match = re.search(r'\b(male|female|man|woman|boy|girl)\b', text_lower)
    age = age_match.group(1) if age_match else "Unknown"
    gender = gender_match.group(1).capitalize() if gender_match else "Unknown"

    # Subjective: extract complaints
    complaint_keywords = ["reports", "complains", "feels", "experiencing", "describes", "noted", "states", "says"]
    subjective_lines = []
    for sentence in text.split('.'):
        if any(kw in sentence.lower() for kw in complaint_keywords):
            subjective_lines.append(sentence.strip())
    subjective = " ".join(subjective_lines[:3]) if subjective_lines else text[:200]

    # Objective: extract vitals/measurements
    vitals = []
    bp_match  = re.search(r'blood pressure[^\d]*(\d+)[/ ](\d+)', text_lower)
    gluc_match= re.search(r'(blood glucose|glucose|sugar)[^\d]*(\d+)', text_lower)
    temp_match= re.search(r'temperature[^\d]*([\d.]+)', text_lower)
    if bp_match:   vitals.append(f"BP: {bp_match.group(1)}/{bp_match.group(2)} mmHg")
    if gluc_match: vitals.append(f"Blood Glucose: {gluc_match.group(2)} mg/dL")
    if temp_match: vitals.append(f"Temperature: {temp_match.group(1)}°C")
    objective = ", ".join(vitals) if vitals else "Vitals not explicitly mentioned in transcript."

    # Assessment: detect conditions
    conditions = []
    cond_map = {
        "diabetes": "Type 2 Diabetes Mellitus",
        "hypertension": "Hypertension", 
        "blood pressure": "Possible Hypertension",
        "chest pain": "Chest Pain — rule out Angina/ACS",
        "shortness of breath": "Dyspnea — assess for cardiac/pulmonary cause",
        "depression": "Major Depressive Disorder",
        "fever": "Pyrexia", 
        "infection": "Possible Infection",
        "fatigue": "Fatigue — assess for anaemia/thyroid",
        "headache": "Cephalgia", 
        "cough": "Productive/non-productive cough",
    }
