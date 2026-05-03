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
        if verified_docs:
            st.markdown(f"##### ✅ Verified Doctors ({len(verified_docs)})")
            for email, doc in verified_docs.items():
                with st.expander(f"✅  {doc['name']}  —  {doc.get('specialty','N/A')}  —  {doc.get('hospital','N/A')}"):
                    col1,col2,col3 = st.columns(3)
                    col1.markdown(f"**🪪 Licence:** {doc.get('licence_no','N/A')}")
                    col2.markdown(f"**✅ Verified by:** {doc.get('verified_by','N/A')}")
                    col3.markdown(f"**📅 Verified at:** {doc.get('verified_at','N/A')}")
                    if doc.get("admin_note"):
                        st.markdown(f"**📝 Note:** {doc['admin_note']}")

                    if st.button(f"🔄 Revoke Verification", key=f"revoke_{email}"):
                        st.session_state.users_db[email]["verified"] = False
                        st.warning(f"Verification revoked for Dr. {doc['name']}.")
                        st.rerun()
    with tab2:
        st.markdown("#### 👥 All Registered Users")

        # Filter controls
        col_f1, col_f2 = st.columns(2)
        filter_role   = col_f1.selectbox("Filter by Role", ["All","User","Doctor","Admin"])
        filter_search = col_f2.text_input("Search by name or email", placeholder="Search...")

        for email, info in db.items():
            # Apply filters
            if filter_role != "All" and info["role"] != filter_role:
                continue
            if filter_search and filter_search.lower() not in email.lower() \
               and filter_search.lower() not in info["name"].lower():
                continue

            role_icon  = {"User":"👤","Doctor":"🩺","Admin":"⚙️"}.get(info["role"],"👤")
            ver_badge  = "✅" if info.get("verified") else "⏳"
            with st.expander(f"{role_icon}  {info['name']}  ({email})  —  {info['role']}  {ver_badge}"):
                col1,col2,col3 = st.columns(3)
                col1.markdown(f"**Role:** {info['role']}")
                col2.markdown(f"**Status:** {'✅ Active' if info.get('verified') else '⏳ Pending'}")
                col3.markdown(f"**Joined:** {info.get('created_at','N/A')}")

                # Role change
                new_role = col1.selectbox(
                    "Change Role",
                    ["User","Doctor","Admin"],
                    index=["User","Doctor","Admin"].index(info["role"]),
                    key=f"role_{email}"
                )
                if col2.button("💾 Update Role", key=f"upd_{email}"):
                    if email == "admin@demo.com":
                        st.warning("Cannot change primary admin role.")
                    else:
                        st.session_state.users_db[email]["role"] = new_role
                        st.success(f"Role updated for {info['name']}")
                        st.rerun()

                if col3.button("🗑️ Delete User", key=f"del_{email}"):
                    if email == "admin@demo.com":
                        st.warning("Cannot delete the primary admin account.")
                    else:
                        del st.session_state.users_db[email]
                        st.success(f"User {info['name']} deleted.")
                        st.rerun()

    # ══════════════════════════════════════════════════════
    # TAB 3 — ANALYTICS
    # ══════════════════════════════════════════════════════
    with tab3:
        st.markdown("#### 📊 System Analytics")
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Total Users",   len(db))
        col2.metric("Doctors",       len(doctors))
        col3.metric("Chat Sessions", len(st.session_state.chat_history)//2)
        col4.metric("Health Logs",   len(st.session_state.health_logs))

        # Role distribution pie
        col_a, col_b = st.columns(2)
        with col_a:
            role_counts = {"User":len(users),"Doctor":len(doctors),
                           "Admin":sum(1 for u in db.values() if u["role"]=="Admin")}
            fig = go.Figure(go.Pie(
                labels=list(role_counts.keys()),
                values=list(role_counts.values()),
                hole=0.45,
                marker_colors=["#42a5f5","#66bb6a","#ef5350"]
            ))
            fig.update_layout(title="Users by Role", height=280,
                              margin=dict(l=10,r=10,t=40,b=10),
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            features = ["Dashboard","Chatbot","Symptoms","Reports","Genetic","Nutrition","Predictions"]
            usage    = [145,98,112,67,45,88,73]
            fig2 = go.Figure(go.Bar(
                x=usage, y=features, orientation="h",
                marker_color=["#2c5364","#43a047","#1e88e5","#fb8c00",
                               "#e53935","#8e24aa","#00acc1"]
            ))
            fig2.update_layout(title="Feature Usage", height=280,
                               plot_bgcolor="#fafcff", paper_bgcolor="rgba(0,0,0,0)",
                               margin=dict(l=10,r=10,t=40,b=10))
            st.plotly_chart(fig2, use_container_width=True)

    # ══════════════════════════════════════════════════════
    # TAB 4 — PERMISSIONS MATRIX
    # ══════════════════════════════════════════════════════
    with tab4:
        st.markdown("#### 🔐 Role-Based Access Permissions")
        st.markdown('<div class="alert-blue">This matrix shows which roles can access which features.</div>',
                    unsafe_allow_html=True)
        st.markdown("")

        permissions = {
            "View Dashboard":            {"User":True,  "Doctor":True,  "Admin":True},
            "AI Disease Prediction":     {"User":True,  "Doctor":True,  "Admin":True},
            "Report Simplifier":         {"User":True,  "Doctor":True,  "Admin":True},
            "Health Chatbot":            {"User":True,  "Doctor":False, "Admin":True},
            "Genetic & AQI Alerts":      {"User":True,  "Doctor":False, "Admin":True},
            "Smart Nutrition":           {"User":True,  "Doctor":False, "Admin":True},
            "Health vs Wealth Charts":   {"User":True,  "Doctor":False, "Admin":True},
            "Voice to Text / SOAP":      {"User":True,  "Doctor":True,  "Admin":False},
            "Doctor Clinical Panel":     {"User":False, "Doctor":True,  "Admin":True},
            "Verify AI Predictions":     {"User":False, "Doctor":True,  "Admin":True},
            "Admin Control Panel":       {"User":False, "Doctor":False, "Admin":True},
            "Manage Users / Roles":      {"User":False, "Doctor":False, "Admin":True},
            "Doctor Verification":       {"User":False, "Doctor":False, "Admin":True},
        }

        # Header
        h1,h2,h3,h4 = st.columns([3,1,1,1])
        h1.markdown("**Feature**")
        h2.markdown("**👤 User**")
        h3.markdown("**🩺 Doctor**")
        h4.markdown("**⚙️ Admin**")
        st.divider()

        for feature, roles in permissions.items():
            c1,c2,c3,c4 = st.columns([3,1,1,1])
            c1.markdown(feature)
            c2.markdown("✅" if roles["User"]   else "❌")
            c3.markdown("✅" if roles["Doctor"] else "❌")
            c4.markdown("✅" if roles["Admin"]  else "❌")

