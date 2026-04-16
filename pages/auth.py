import streamlit as st

def show():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 30px 0 20px 0;">
            <div style="display:inline-block; background:linear-gradient(135deg,#0f2027,#2c5364);
                        border-radius:20px; padding:16px 32px; margin-bottom:16px;
                        box-shadow:0 8px 24px rgba(44,83,100,0.35);">
                <h1 style="color:white; font-size:2.2rem; margin:0;">🏥 NLP-Medora</h1>
            </div>
            <p style="color:#546e7a; font-size:1.05rem; margin-top:8px;">
                AI-Powered Health Management Dashboard
            </p>
        </div>
        <style>
        /* Auth-specific: wrap tabs in a card */
        div[data-testid="column"] > div > div > div > div[data-baseweb="tab-panel"] {
            background: white !important;
            border-radius: 0 0 16px 16px !important;
            padding: 20px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            st.markdown("### Welcome Back")
            email = st.text_input("Email", placeholder="patient@demo.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")

            st.markdown("""
            <div class="alert-blue" style="margin:8px 0 12px 0;">
            <b>Demo Credentials:</b><br>
            👤 patient@demo.com / patient123<br>
            🩺 doctor@demo.com / doctor123<br>
            ⚙️ admin@demo.com / admin123
            </div>
            """, unsafe_allow_html=True)

            if st.button("Login", use_container_width=True, key="btn_login"):
                db = st.session_state.users_db
                if email in db and db[email]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_role = db[email]["role"]
                    st.session_state.username = db[email]["name"]
                    st.session_state.current_page = "dashboard"
                    st.success(f"✅ Welcome, {db[email]['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Try demo accounts above.")

        with tab2:
            st.markdown("### Create Account")
            name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            role = st.selectbox("Role", ["User", "Doctor"], key="reg_role")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            reg_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2")

            if st.button("Register", use_container_width=True, key="btn_register"):
                if not all([name, reg_email, reg_pass]):
                    st.error("Please fill all fields.")
                elif reg_pass != reg_pass2:
                    st.error("Passwords do not match.")
                elif reg_email in st.session_state.users_db:
                    st.error("Email already registered.")
                else:
                    st.session_state.users_db[reg_email] = {
                        "password": reg_pass,
                        "role": role,
                        "name": name,
                        "verified": role == "User"
                    }
                    st.success("✅ Account created! Please login.")