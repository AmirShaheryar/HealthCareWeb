import streamlit as st

def show():
    st.title("📋 Your Medical Notes")

    user_email = st.session_state.get("user_email")

    notes = st.session_state.get("shared_notes", [])

    patient_notes = [n for n in notes if n["email"] == user_email]

    if not patient_notes:
        st.info("No notes from doctor yet.")
        return

    for note in reversed(patient_notes):
        with st.expander(f"{note['type']} — {note['timestamp']}"):
            st.markdown(f"**Doctor:** {note['doctor']}")
            st.markdown(f"**Patient:** {note['patient']}")
            st.text(note["content"])
