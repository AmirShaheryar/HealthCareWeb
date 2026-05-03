import streamlit as st
from datetime import datetime

def show():
    # 🔐 Role Check
    if st.session_state.get("user_role") != "Doctor":
        st.warning("🚫 This section is restricted to Doctors only.")
        return

    st.markdown('<p class="section-title">🩺 Doctor Clinical Panel</p>', unsafe_allow_html=True)
    st.markdown(f"Welcome, **{st.session_state.get('username','Doctor')}**. Review AI-generated patient predictions below.")

    # 🔹 Ensure shared storage exists
    if "prediction_requests" not in st.session_state:
        st.session_state.prediction_requests = []

    if "shared_notes" not in st.session_state:
        st.session_state.shared_notes = []

    reqs = st.session_state.prediction_requests
    pending   = [r for r in reqs if r["status"] == "Pending"]
    reviewed  = [r for r in reqs if r["status"] in ["Verified","Rejected"]]

    # ── Summary ─────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📋 Total Requests", len(reqs))
    c2.metric("⏳ Pending", len(pending))
    c3.metric("✅ Verified", len([r for r in reviewed if r["status"]=="Verified"]))
    c4.metric("❌ Rejected", len([r for r in reviewed if r["status"]=="Rejected"]))

    st.divider()

    tab1, tab2, tab3 = st.tabs([
        f"⏳ Pending ({len(pending)})",
        f"✅ Reviewed ({len(reviewed)})",
        "📝 Write Clinical Note"
    ])

    # ══════════════════════════════════════════════════════
    # TAB 1 — PENDING
    # ══════════════════════════════════════════════════════
    with tab1:
        if not pending:
            st.success("✅ No pending requests.")
        else:
            for req in pending:
                with st.expander(f"{req['id']} — {req['patient_name']} — {req['ai_prediction']}"):
                    
                    st.write(f"**Patient:** {req['patient_name']}")
                    st.write(f"**Email:** {req['patient_email']}")
                    st.write(f"**AI Diagnosis:** {req['ai_prediction']}")
                    st.write(f"**Confidence:** {req['ai_confidence']}%")

                    st.write("**Symptoms:**", ", ".join(req["symptoms"]))

                    # ── Doctor Input ─────────────────────────
                    agree = st.radio(
                        "Agree with AI?",
                        ["Yes", "Modify", "No"],
                        key=f"agree_{req['id']}"
                    )

                    final_diagnosis = req["ai_prediction"]
                    if agree != "Yes":
                        final_diagnosis = st.text_input(
                            "Final Diagnosis",
                            value=req["ai_prediction"],
                            key=f"diag_{req['id']}"
                        )

                    note = st.text_area(
                        "Doctor Note",
                        key=f"note_{req['id']}"
                    )

                    severity = st.selectbox(
                        "Severity",
                        ["Mild","Moderate","Severe","Critical"],
                        key=f"sev_{req['id']}"
                    )

                    col1, col2 = st.columns(2)

                    # ✅ VERIFY
                    if col1.button("✅ Verify", key=f"v_{req['id']}"):
                        for i, r in enumerate(st.session_state.prediction_requests):
                            if r["id"] == req["id"]:
                                st.session_state.prediction_requests[i].update({
                                    "status": "Verified",
                                    "final_diagnosis": final_diagnosis,
                                    "doctor_note": note,
                                    "severity": severity,
                                    "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                                })

                                # 🔥 SEND NOTE TO PATIENT
                                st.session_state.shared_notes.append({
                                    "patient": req["patient_name"],
                                    "email": req["patient_email"],
                                    "type": "AI Diagnosis Review",
                                    "content": f"""
Diagnosis: {final_diagnosis}

Severity: {severity}

Doctor Notes:
{note}
""",
                                    "doctor": st.session_state.get("username"),
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                })
                                break

                        st.success("✅ Verified & sent to patient")
                        st.rerun()

                    # ❌ REJECT
                    if col2.button("❌ Reject", key=f"r_{req['id']}"):
                        for i, r in enumerate(st.session_state.prediction_requests):
                            if r["id"] == req["id"]:
                                st.session_state.prediction_requests[i]["status"] = "Rejected"
                                break

                        st.warning("❌ Request Rejected")
                        st.rerun()

    # ══════════════════════════════════════════════════════
    # TAB 2 — REVIEWED
    # ══════════════════════════════════════════════════════
    with tab2:
        if not reviewed:
            st.info("No reviewed cases.")
        else:
            for req in reviewed:
                with st.expander(f"{req['id']} — {req['patient_name']}"):
                    st.write(f"Final Diagnosis: {req.get('final_diagnosis')}")
                    st.write(f"Doctor Note: {req.get('doctor_note')}")
                    st.write(f"Severity: {req.get('severity')}")

    # ══════════════════════════════════════════════════════
    # TAB 3 — WRITE NOTE
    # ══════════════════════════════════════════════════════
    with tab3:
        with st.form("note_form"):
            patient_name  = st.text_input("Patient Name")
            patient_email = st.text_input("Patient Email")
            note_type     = st.selectbox("Type", ["SOAP", "Prescription", "General"])
            content       = st.text_area("Write Note")

            if st.form_submit_button("💾 Save & Send"):
                st.session_state.shared_notes.append({
                    "patient": patient_name,
                    "email": patient_email,
                    "type": note_type,
                    "content": content,
                    "doctor": st.session_state.get("username"),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

                st.success("✅ Note sent to patient!")
