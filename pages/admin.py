import streamlit as st
import plotly.graph_objects as go

def show():
    if st.session_state.user_role != "Admin":
        st.warning("🚫 This section is restricted to Admins only.")
        return

    st.markdown('<p class="section-title">⚙️ Admin Control Panel</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 System Analytics", "🔐 Permissions"])

    with tab1:
        st.markdown("#### Registered Users")
        db = st.session_state.users_db

        for email, info in db.items():
            role_badge = {"User": "🟢", "Doctor": "🔵", "Admin": "🔴"}.get(info["role"], "⚪")
            verified_badge = "✅ Verified" if info.get("verified") else "⏳ Pending"
            with st.expander(f"{role_badge} **{info['name']}** ({email}) — {info['role']} — {verified_badge}"):
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"**Role:** {info['role']}")
                col2.markdown(f"**Status:** {verified_badge}")

                if not info.get("verified") and info["role"] == "Doctor":
                    if col3.button(f"✅ Verify Doctor", key=f"ver_{email}"):
                        st.session_state.users_db[email]["verified"] = True
                        st.success(f"Doctor {info['name']} verified!")
                        st.rerun()

                new_role = col1.selectbox("Change Role", ["User", "Doctor", "Admin"],
                                           index=["User", "Doctor", "Admin"].index(info["role"]),
                                           key=f"role_{email}")
                if col2.button("💾 Update Role", key=f"upd_{email}"):
                    if email != "admin@demo.com":  # protect main admin
                        st.session_state.users_db[email]["role"] = new_role
                        st.success(f"Role updated for {info['name']}")
                        st.rerun()
                    else:
                        st.warning("Cannot change primary admin role.")

                if col3.button("🗑️ Remove User", key=f"del_{email}"):
                    if email != "admin@demo.com":
                        del st.session_state.users_db[email]
                        st.success(f"User {info['name']} removed.")
                        st.rerun()
                    else:
                        st.warning("Cannot delete the admin account.")

    with tab2:
        st.markdown("#### System Usage Analytics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Users", len(st.session_state.users_db))
        col2.metric("Doctors", sum(1 for u in st.session_state.users_db.values() if u["role"] == "Doctor"))
        col3.metric("Chat Sessions", len(st.session_state.chat_history) // 2)
        col4.metric("Health Logs", len(st.session_state.health_logs))

        # Simulated usage bar chart
        features = ["Dashboard", "Chatbot", "Symptom DB", "Report Simplifier", "Genetic AQI", "Nutrition", "Predictions"]
        usage = [145, 98, 112, 67, 45, 88, 73]
        fig = go.Figure(go.Bar(x=features, y=usage,
                                marker_color=["#2c5364","#43a047","#1e88e5","#fb8c00","#e53935","#8e24aa","#00acc1"]))
        fig.update_layout(title="Feature Usage (Simulated)", height=300,
                          plot_bgcolor="#fafcff", paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("#### 🔐 System Permission Settings")
        st.markdown("""
        <div class="alert-blue">
        Configure which roles can access which features.
        </div>
        """, unsafe_allow_html=True)

        permissions = {
            "View Dashboard":       {"User": True,  "Doctor": True,  "Admin": True},
            "AI Disease Prediction":{"User": True,  "Doctor": True,  "Admin": True},
            "Report Simplifier":    {"User": True,  "Doctor": True,  "Admin": True},
            "Genetic AQI Alerts":   {"User": True,  "Doctor": False, "Admin": True},
            "Doctor Panel":         {"User": False, "Doctor": True,  "Admin": True},
            "Admin Panel":          {"User": False, "Doctor": False, "Admin": True},
            "Delete Users":         {"User": False, "Doctor": False, "Admin": True},
        }

        for feature, roles in permissions.items():
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown(f"**{feature}**")
            for i, (role, allowed) in enumerate(roles.items()):
                icon = "✅" if allowed else "❌"
                cols[i+1].markdown(f"{icon} {role}")

        st.caption("Permission matrix is for display. Full RBAC implementation uses database-backed policy engine.")
