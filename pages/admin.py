import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

def show():
    if st.session_state.user_role != "Admin":
        st.warning("🚫 This section is restricted to Admins only.")
        return

    st.markdown('<p class="section-title">⚙️ Admin Control Panel</p>', unsafe_allow_html=True)
    st.markdown(f"Welcome, **{st.session_state.username}**. Manage users, verify doctors, and control permissions.")

    db = st.session_state.users_db

    # ── Summary metrics ────────────────────────────────────────────────────────
    total     = len(db)
    doctors   = [e for e,u in db.items() if u["role"]=="Doctor"]
    pending   = [e for e in doctors if not db[e].get("verified")]
    users     = [e for e,u in db.items() if u["role"]=="User"]

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("👥 Total Users",      total)
    col2.metric("🩺 Doctors",          len(doctors))
    col3.metric("⏳ Pending Verification", len(pending),
                delta=f"{len(pending)} need action" if pending else None,
                delta_color="inverse")
    col4.metric("👤 Patients",         len(users))

    if pending:
        st.markdown(f"""
        <div class="alert-amber">
        ⚠️ <b>{len(pending)} doctor(s)</b> are awaiting licence verification.
        Review them in the <b>Doctor Verification</b> tab below.
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "⏳ Doctor Verification",
        "👥 User Management",
        "📊 Analytics",
        "🔐 Permissions"
    ])

    with tab1:
        st.markdown("#### 🩺 Doctor Licence Verification")

        pending_docs   = {e:db[e] for e in doctors if not db[e].get("verified")}
        verified_docs  = {e:db[e] for e in doctors if db[e].get("verified")}

        # ── Pending ────────────────────────────────────────────────────────────
        if pending_docs:
            st.markdown(f"##### ⏳ Pending ({len(pending_docs)})")
            for email, doc in pending_docs.items():
                with st.expander(f"⏳  {doc['name']}  —  {doc.get('specialty','N/A')}  —  {email}"):
                    col1, col2, col3 = st.columns(3)
                    col1.markdown(f"**👤 Name:** {doc['name']}")
                    col2.markdown(f"**📧 Email:** {email}")
                    col3.markdown(f"**🔬 Specialty:** {doc.get('specialty','N/A')}")
                    col1.markdown(f"**🏥 Hospital:** {doc.get('hospital','N/A')}")
                    col2.markdown(f"**🪪 Licence No:** {doc.get('licence_no','N/A')}")
                    col3.markdown(f"**📅 Applied:** {doc.get('created_at','N/A')}")
                    if doc.get("education"):
                        st.markdown(f"**🎓 Education:** {doc['education']}")

                    st.markdown("")
                    admin_note = st.text_input("Admin Note (optional):",
                                               placeholder="e.g. Licence verified via PMDC portal",
                                               key=f"note_{email}")
                    c1, c2, c3 = st.columns(3)

                    if c1.button("✅ Approve", key=f"approve_{email}", use_container_width=True):
                        st.session_state.users_db[email]["verified"]       = True
                        st.session_state.users_db[email]["verified_by"]    = st.session_state.username
                        st.session_state.users_db[email]["verified_at"]    = datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.session_state.users_db[email]["admin_note"]     = admin_note
                        st.success(f"✅ Dr. {doc['name']} has been approved.")
                        st.rerun()

                    if c2.button("❌ Reject", key=f"reject_{email}", use_container_width=True):
                        st.session_state.users_db[email]["verified"]    = False
                        st.session_state.users_db[email]["rejected"]    = True
                        st.session_state.users_db[email]["admin_note"]  = admin_note
                        st.warning(f"Dr. {doc['name']} application rejected.")
                        st.rerun()

                    if c3.button("🔎 Request More Info", key=f"info_{email}", use_container_width=True):
                        st.info(f"Info request sent to {email}.")
        else:
            st.markdown('<div class="alert-green">✅ No pending verifications.</div>',
                        unsafe_allow_html=True)
