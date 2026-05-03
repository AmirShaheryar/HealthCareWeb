import streamlit as st
import bcrypt
import re
from datetime import datetime

# ── Password helpers ──────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def check_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        # fallback for demo plain-text passwords already in session
        return plain == hashed

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$", email))

def password_strength(pw: str):
    score = 0
    tips  = []
    if len(pw) >= 8:        score += 1
    else:                   tips.append("At least 8 characters")
    if re.search(r'[A-Z]', pw): score += 1
    else:                   tips.append("One uppercase letter")
    if re.search(r'[0-9]', pw): score += 1
    else:                   tips.append("One number")
    if re.search(r'[^A-Za-z0-9]', pw): score += 1
    else:                   tips.append("One special character")
    labels = ["", "Weak", "Fair", "Good", "Strong"]
    colors = ["", "#e53935", "#fb8c00", "#fdd835", "#43a047"]
    return score, labels[score] if score else "Weak", colors[score] if score else "#e53935", tips

# ── Seed hashed demo passwords on first run ───────────────────────────────────
def seed_demo_users():
    if "users_seeded" not in st.session_state:
        for email, data in st.session_state.users_db.items():
            pw = data["password"]
            # Only hash if not already hashed
            if not pw.startswith("$2b$"):
                st.session_state.users_db[email]["password"] = hash_password(pw)
        st.session_state.users_seeded = True

def show():
    seed_demo_users()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # ── Header ────────────────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; padding:30px 0 20px 0;">
            <div style="display:inline-block;
                        background:linear-gradient(135deg,#0f2027,#2c5364);
                        border-radius:20px; padding:16px 40px; margin-bottom:12px;
                        box-shadow:0 8px 24px rgba(44,83,100,0.35);">
                <h1 style="color:white;font-size:2.2rem;margin:0;">🏥 NLP-Medora</h1>
            </div>
            <p style="color:#546e7a;font-size:1rem;margin-top:6px;">
                AI-Powered Health Management Dashboard
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

            with tab_login:
            st.markdown("### Welcome Back")

            # Demo credentials box
            st.markdown("""
            <div class="alert-blue">
            <b>🔑 Demo Credentials:</b><br>
            👤 patient@demo.com &nbsp;/&nbsp; patient123<br>
            🩺 doctor@demo.com &nbsp;/&nbsp; doctor123<br>
            ⚙️ admin@demo.com &nbsp;/&nbsp; admin123
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")

            email    = st.text_input("📧 Email Address", placeholder="you@example.com", key="login_email")
            password = st.text_input("🔒 Password", type="password", key="login_pass")

            col_a, col_b = st.columns([3, 1])
            login_btn = col_a.button("Login →", use_container_width=True, key="btn_login")

            if login_btn:
                if not email or not password:
                    st.error("Please enter both email and password.")
                elif not is_valid_email(email):
                    st.error("Please enter a valid email address.")
                else:
                    db = st.session_state.users_db
                    if email in db and check_password(password, db[email]["password"]):
                        user = db[email]
                        if not user.get("verified", False) and user["role"] == "Doctor":
                            st.warning("⏳ Your doctor account is pending admin verification. Please wait.")
                        else:
                            st.session_state.logged_in     = True
                            st.session_state.user_role     = user["role"]
                            st.session_state.username      = user["name"]
                            st.session_state.user_email    = email
                            st.session_state.current_page  = "dashboard"
                            # Log login time
                            st.session_state.users_db[email]["last_login"] = \
                                datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.success(f"✅ Welcome back, {user['name']}!")
                            st.rerun()
                    else:
                        st.error("❌ Invalid email or password.")

        # ════════════════════════════════════════════════
        # TAB 2 — REGISTER
        # ════════════════════════════════════════════════
        with tab_register:
            st.markdown("### Create Your Account")

            name      = st.text_input("👤 Full Name", placeholder="Ali Raza", key="reg_name")
            reg_email = st.text_input("📧 Email Address", placeholder="ali@example.com", key="reg_email")
            role      = st.selectbox("🏷️ Register As", ["User (Patient)", "Doctor"], key="reg_role")

            # Doctor-specific fields
            if role == "Doctor":
                st.markdown("""
                <div class="alert-amber">
                🩺 <b>Doctor accounts require admin verification</b> before login is granted.
                Please provide your licence details below.
                </div>
                """, unsafe_allow_html=True)
                lic_no   = st.text_input("🪪 Medical Licence Number", placeholder="e.g. PMDC-12345", key="reg_lic")
                hospital = st.text_input("🏥 Hospital / Clinic Name", placeholder="e.g. Shaukat Khanum", key="reg_hosp")
                specialty= st.selectbox("🔬 Specialty", [
                    "General Physician","Cardiologist","Dermatologist","Neurologist",
                    "Endocrinologist","Psychiatrist","Orthopedic","Pediatrician","Other"
                ], key="reg_spec")
            else:
                lic_no = hospital = specialty = ""

            reg_pass  = st.text_input("🔒 Password", type="password", key="reg_pass")

            # Live password strength meter
            if reg_pass:
                score, label, color, tips = password_strength(reg_pass)
                filled   = "█" * score
                unfilled = "░" * (4 - score)
                st.markdown(
                    f'<div style="margin:4px 0 2px 0;">'
                    f'<span style="color:{color};font-weight:700;">{filled}{unfilled} {label}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if tips:
                    st.caption("Missing: " + " · ".join(tips))

            reg_pass2 = st.text_input("🔒 Confirm Password", type="password", key="reg_pass2")

            # Terms checkbox
            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="reg_terms")

            if st.button("Create Account", use_container_width=True, key="btn_register"):
                # Validation
                errors = []
                if not name.strip():             errors.append("Full name is required.")
                if not is_valid_email(reg_email):errors.append("Enter a valid email address.")
                if reg_email in st.session_state.users_db:
                                                 errors.append("This email is already registered.")
                if len(reg_pass) < 6:            errors.append("Password must be at least 6 characters.")
                if reg_pass != reg_pass2:        errors.append("Passwords do not match.")
                if not agree:                    errors.append("You must agree to the Terms of Service.")
                if role == "Doctor" and not lic_no.strip():
                                                 errors.append("Medical licence number is required for doctors.")

                if errors:
                    for err in errors:
                        st.error(f"❌ {err}")
                else:
                    actual_role = "Doctor" if role == "Doctor" else "User"
                    st.session_state.users_db[reg_email] = {
                        "password":    hash_password(reg_pass),
                        "role":        actual_role,
                        "name":        name.strip(),
                        "verified":    actual_role == "User",   # Doctors need admin verification
                        "created_at":  datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "last_login":  None,
                        "licence_no":  lic_no,
                        "hospital":    hospital,
                        "specialty":   specialty,
                        "bio":         "",
                        "phone":       "",
                        "dob":         "",
                        "blood_group": "",
                        "allergies":   "",
                        "conditions":  "",
                        "emergency_contact": "",
                    }
                    if actual_role == "Doctor":
                        st.success("✅ Doctor account created! Please wait for admin verification before logging in.")
                    else:
                        st.success("✅ Account created successfully! You can now login.")
