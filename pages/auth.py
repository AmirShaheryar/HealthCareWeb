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

