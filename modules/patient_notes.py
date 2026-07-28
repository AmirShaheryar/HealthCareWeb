import streamlit as st
from modules.db import get_clinical_notes_for_email

def show():
    st.title("📋 Your Medical Notes")

    user_email = st.session_state.get("user_email")

    patient_notes = get_clinical_notes_for_email(user_email) if user_email else []

    if not patient_notes:
        st.info("No notes from doctor yet.")
        return

    for note in reversed(patient_notes):
        with st.expander(f"{note['type']} — {note['timestamp']}"):
            st.markdown(f"**Doctor:** {note['doctor']}")
            st.markdown(f"**Patient:** {note['patient']}")
            st.text(note["content"])