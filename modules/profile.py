import streamlit as st
from datetime import datetime
from modules.auth import hash_password, check_password, password_strength
from modules.db import upsert_user

def show():
    st.markdown('<p class="section-title">👤 Profile Management</p>', unsafe_allow_html=True)
    email = st.session_state.get("user_email", "")
    role  = st.session_state.user_role
    db    = st.session_state.users_db

    if email not in db:
        st.error("Session error. Please log in again.")
        return

    user = db[email]

    # ── Profile header card ────────────────────────────────────────────────────
    role_icon = {"User":"👤","Doctor":"🩺","Admin":"⚙️"}.get(role,"👤")
    verified  = "✅ Verified" if user.get("verified") else "⏳ Pending Verification"
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0f2027,#2c5364);
                border-radius:16px;padding:24px 28px;color:white;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="font-size:3rem;">{role_icon}</div>
            <div>
                <h2 style="margin:0;color:white;">{user['name']}</h2>
                <p style="margin:4px 0 0 0;opacity:0.8;">{email} &nbsp;|&nbsp; {role} &nbsp;|&nbsp; {verified}</p>
                <p style="margin:4px 0 0 0;opacity:0.6;font-size:0.85rem;">
                    Member since: {user.get('created_at','N/A')} &nbsp;|&nbsp;
                    Last login: {user.get('last_login','N/A')}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs by role ──────────────────────────────────────────────────────────
    if role == "User":
        tab1, tab2, tab3 = st.tabs(["📋 Personal Info", "🩺 Health Data", "🔒 Security"])
        _user_personal_tab(tab1, email, user)
        _user_health_tab(tab2, email, user)
        _security_tab(tab3, email, user)

    elif role == "Doctor":
        tab1, tab2, tab3 = st.tabs(["📋 Personal Info", "🏥 Medical Credentials", "🔒 Security"])
        _user_personal_tab(tab1, email, user)
        _doctor_credentials_tab(tab2, email, user)
        _security_tab(tab3, email, user)

    elif role == "Admin":
        tab1, tab2 = st.tabs(["📋 Personal Info", "🔒 Security"])
        _user_personal_tab(tab1, email, user)
        _security_tab(tab2, email, user)


# ── Personal info tab (all roles) ─────────────────────────────────────────────
def _user_personal_tab(tab, email, user):
    with tab:
        st.markdown("#### Update Personal Information")
        with st.form("personal_form"):
            col1, col2 = st.columns(2)
            name  = col1.text_input("Full Name",  value=user.get("name",""))
            phone = col2.text_input("Phone Number", value=user.get("phone",""),
                                    placeholder="+92-300-0000000")
            dob   = col1.text_input("Date of Birth", value=user.get("dob",""),
                                    placeholder="YYYY-MM-DD")
            blood = col2.selectbox("Blood Group",
                                   ["","A+","A-","B+","B-","AB+","AB-","O+","O-"],
                                   index=["","A+","A-","B+","B-","AB+","AB-","O+","O-"]
                                   .index(user.get("blood_group","")) if user.get("blood_group","") in
                                   ["","A+","A-","B+","B-","AB+","AB-","O+","O-"] else 0)
            emergency = st.text_input("Emergency Contact",
                                      value=user.get("emergency_contact",""),
                                      placeholder="Name — Phone Number")
            bio = st.text_area("Bio / Notes", value=user.get("bio",""),
                               placeholder="Brief description...", height=80)

            if st.form_submit_button("💾 Save Personal Info", use_container_width=True):
                st.session_state.users_db[email].update({
                    "name": name, "phone": phone, "dob": dob,
                    "blood_group": blood, "emergency_contact": emergency, "bio": bio,
                })
                upsert_user(email, st.session_state.users_db[email])
                st.session_state.username = name
                st.success("✅ Personal information updated!")


# ── Health data tab (User role) ────────────────────────────────────────────────
def _user_health_tab(tab, email, user):
    with tab:
        st.markdown("#### Update Health Information")
        with st.form("health_form"):
            col1, col2, col3 = st.columns(3)
            height  = col1.number_input("Height (cm)", 100, 250,
                                        int(user.get("height",170) or 170))
            weight  = col2.number_input("Weight (kg)", 20, 300,
                                        int(user.get("weight",70) or 70))
            # Auto-calculate BMI
            bmi = round(weight / ((height/100)**2), 1) if height > 0 else 0
            bmi_cat = ("Underweight" if bmi < 18.5 else
                       "Normal" if bmi < 25 else
                       "Overweight" if bmi < 30 else "Obese")
            col3.metric("BMI", f"{bmi}", bmi_cat)

            allergies  = st.text_area("Known Allergies",
                                      value=user.get("allergies",""),
                                      placeholder="e.g. Penicillin, Peanuts, Dust",
                                      height=70)
            conditions = st.text_area("Existing Medical Conditions",
                                      value=user.get("conditions",""),
                                      placeholder="e.g. Type 2 Diabetes, Hypertension",
                                      height=70)
            col_a, col_b = st.columns(2)
            smoker    = col_a.selectbox("Smoking Status",
                                        ["Non-smoker","Ex-smoker","Current smoker"],
                                        index=["Non-smoker","Ex-smoker","Current smoker"]
                                        .index(user.get("smoker","Non-smoker"))
                                        if user.get("smoker") in
                                        ["Non-smoker","Ex-smoker","Current smoker"] else 0)
            activity  = col_b.selectbox("Activity Level",
                                        ["Sedentary","Lightly active","Moderately active","Very active"],
                                        index=["Sedentary","Lightly active","Moderately active","Very active"]
                                        .index(user.get("activity","Sedentary"))
                                        if user.get("activity") in
                                        ["Sedentary","Lightly active","Moderately active","Very active"] else 0)

            if st.form_submit_button("💾 Save Health Data", use_container_width=True):
                st.session_state.users_db[email].update({
                    "height": height, "weight": weight, "bmi": bmi,
                    "allergies": allergies, "conditions": conditions,
                    "smoker": smoker, "activity": activity,
                })
                upsert_user(email, st.session_state.users_db[email])
                st.success("✅ Health data updated!")

        # Health summary cards
        if user.get("height") and user.get("weight"):
            st.markdown("#### 📊 Health Summary")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Height", f"{user.get('height','—')} cm")
            c2.metric("Weight", f"{user.get('weight','—')} kg")
            c3.metric("BMI",    f"{user.get('bmi','—')}")
            c4.metric("Blood",  user.get('blood_group','—'))


# ── Doctor credentials tab ─────────────────────────────────────────────────────
def _doctor_credentials_tab(tab, email, user):
    with tab:
        st.markdown("#### Manage Medical Credentials")

        verified = user.get("verified", False)
        if verified:
            st.markdown('<div class="alert-green">✅ Your credentials are <b>verified</b> by admin.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-amber">⏳ Your credentials are <b>pending admin verification</b>.</div>',
                        unsafe_allow_html=True)

        st.markdown("")
        with st.form("credentials_form"):
            col1, col2 = st.columns(2)
            lic_no    = col1.text_input("Medical Licence Number",
                                        value=user.get("licence_no",""),
                                        placeholder="PMDC-12345")
            specialty = col2.selectbox("Specialty",
                                       ["General Physician","Cardiologist","Dermatologist",
                                        "Neurologist","Endocrinologist","Psychiatrist",
                                        "Orthopedic","Pediatrician","Other"],
                                       index=["General Physician","Cardiologist","Dermatologist",
                                              "Neurologist","Endocrinologist","Psychiatrist",
                                              "Orthopedic","Pediatrician","Other"]
                                       .index(user.get("specialty","General Physician"))
                                       if user.get("specialty") in
                                       ["General Physician","Cardiologist","Dermatologist",
                                        "Neurologist","Endocrinologist","Psychiatrist",
                                        "Orthopedic","Pediatrician","Other"] else 0)
            hospital  = col1.text_input("Hospital / Clinic",
                                        value=user.get("hospital",""),
                                        placeholder="e.g. Shaukat Khanum Hospital")
            experience= col2.number_input("Years of Experience", 0, 50,
                                          int(user.get("experience", 0) or 0))
            education = st.text_area("Education / Qualifications",
                                     value=user.get("education",""),
                                     placeholder="e.g. MBBS FCPS Cardiology",
                                     height=70)
            bio = st.text_area("Professional Bio",
                               value=user.get("bio",""),
                               placeholder="Brief professional summary...",
                               height=80)

            if st.form_submit_button("💾 Update Credentials", use_container_width=True):
                st.session_state.users_db[email].update({
                    "licence_no": lic_no, "specialty": specialty,
                    "hospital": hospital, "experience": experience,
                    "education": education, "bio": bio,
                })
                upsert_user(email, st.session_state.users_db[email])
                st.success("✅ Credentials updated! Admin will re-verify if changed.")


# ── Security / Change password tab (all roles) ────────────────────────────────
def _security_tab(tab, email, user):
    with tab:
        st.markdown("#### Change Password")
        with st.form("security_form"):
            current_pw = st.text_input("Current Password", type="password", key="cur_pw")
            new_pw     = st.text_input("New Password",     type="password", key="new_pw")

            if new_pw:
                score, label, color, tips = password_strength(new_pw)
                st.markdown(
                    f'<span style="color:{color};font-weight:700;">Password strength: {label}</span>',
                    unsafe_allow_html=True
                )
                if tips:
                    st.caption("Missing: " + " · ".join(tips))

            confirm_pw = st.text_input("Confirm New Password", type="password", key="conf_pw")

            if st.form_submit_button("🔒 Update Password", use_container_width=True):
                if not check_password(current_pw, user["password"]):
                    st.error("❌ Current password is incorrect.")
                elif len(new_pw) < 6:
                    st.error("New password must be at least 6 characters.")
                elif new_pw != confirm_pw:
                    st.error("New passwords do not match.")
                else:
                    st.session_state.users_db[email]["password"] = hash_password(new_pw)
                    upsert_user(email, st.session_state.users_db[email])
                    st.success("✅ Password updated successfully!")

        st.divider()
        st.markdown("#### 🔐 Account Security Info")
        col1, col2, col3 = st.columns(3)
        col1.metric("Account Role",  user.get("role","—"))
        col2.metric("Member Since",  user.get("created_at","—")[:10] if user.get("created_at") else "—")
        col3.metric("Last Login",    user.get("last_login","—")[:10] if user.get("last_login") else "Never")
