import streamlit as st
from modules.db import (
    send_message,
    get_conversation,
    mark_conversation_read,
    get_conversations_for_user,
    get_verified_doctors,
    get_all_patients,
)

try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_AUTOREFRESH = True
except ImportError:
    _HAS_AUTOREFRESH = False


def _init_state():
    if "active_chat_partner" not in st.session_state:
        st.session_state.active_chat_partner = None  # {"email":..., "name":...}


def _contact_list(my_email: str, my_role: str):
    """Everyone this user can message: existing conversations + role-based directory."""
    contacts = {c["email"]: c for c in get_conversations_for_user(my_email)}

    if my_role == "User":
        for doc in get_verified_doctors(st.session_state.users_db):
            contacts.setdefault(doc["email"], {
                "email": doc["email"], "name": doc["name"],
                "last_message": f"{doc.get('specialty','')} · start a conversation",
                "last_timestamp": "", "unread": 0,
            })
    elif my_role == "Doctor":
        for pat in get_all_patients(st.session_state.users_db):
            contacts.setdefault(pat["email"], {
                "email": pat["email"], "name": pat["name"],
                "last_message": "Start a conversation",
                "last_timestamp": "", "unread": 0,
            })

    # Conversations with real activity first, then alphabetical for the rest
    with_activity = [c for c in contacts.values() if c["last_timestamp"]]
    without       = [c for c in contacts.values() if not c["last_timestamp"]]
    with_activity.sort(key=lambda c: c["last_timestamp"], reverse=True)
    without.sort(key=lambda c: c["name"].lower())
    return with_activity + without


def show():
    _init_state()

    my_email = st.session_state.get("user_email", "")
    my_name  = st.session_state.get("username", "")
    my_role  = st.session_state.get("user_role", "")

    if my_role not in ("User", "Doctor"):
        st.warning("🚫 Messaging is available for patients and doctors only.")
        return

    st.markdown('<p class="section-title">💬 Messages</p>', unsafe_allow_html=True)
    other_role_label = "doctor" if my_role == "User" else "patient"
    st.caption(f"Chat directly with your {other_role_label}, just like WhatsApp.")

    # Gentle auto-refresh so new messages show up without a manual reload
    if _HAS_AUTOREFRESH:
        st_autorefresh(interval=4000, key="messages_autorefresh")
    else:
        st.button("🔄 Refresh")

    contacts = _contact_list(my_email, my_role)

    col_list, col_chat = st.columns([1, 2], gap="medium")

    # ══════════════════════════════════════════════════════
    # LEFT — Contact list
    # ══════════════════════════════════════════════════════
    with col_list:
        st.markdown("#### Conversations")
        if not contacts:
            st.info("No contacts yet.")
        search = st.text_input("🔍 Search", key="msg_search", placeholder="Search by name...")

        active = st.session_state.active_chat_partner

        for c in contacts:
            if search and search.lower() not in c["name"].lower():
                continue

            is_active = active is not None and active["email"] == c["email"]
            unread_badge = f" 🔴{c['unread']}" if c.get("unread") else ""
            preview = (c["last_message"] or "")[:38]
            label = f"{'▶ ' if is_active else ''}{c['name']}{unread_badge}\n{preview}"

            if st.button(label, key=f"contact_{c['email']}", use_container_width=True):
                st.session_state.active_chat_partner = {"email": c["email"], "name": c["name"]}
                mark_conversation_read(my_email, c["email"])
                st.rerun()

    # ══════════════════════════════════════════════════════
    # RIGHT — Active chat thread
    # ══════════════════════════════════════════════════════
    with col_chat:
        active = st.session_state.active_chat_partner
        if not active:
            st.info("👈 Select a conversation to start chatting.")
            return

        partner_email = active["email"]
        partner_name  = active["name"]

        st.markdown(f"#### 💬 {partner_name}")
        st.caption(partner_email)

        mark_conversation_read(my_email, partner_email)
        history = get_conversation(my_email, partner_email)

        chat_box = st.container(height=420, border=True)
        with chat_box:
            if not history:
                st.caption("No messages yet — say hello 👋")
            for msg in history:
                bubble_class = "chat-user" if msg["sender_email"] == my_email else "chat-bot"
                align = "text-align:right;" if msg["sender_email"] == my_email else "text-align:left;"
                st.markdown(
                    f"""<div style="{align}">
                        <div class="{bubble_class}" style="display:inline-block;text-align:left;">
                            {msg['content']}
                            <div style="font-size:0.7rem;opacity:0.6;margin-top:4px;">{msg['timestamp']}</div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        with st.form(key=f"send_form_{partner_email}", clear_on_submit=True):
            col_input, col_btn = st.columns([5, 1])
            text = col_input.text_input(
                "Type a message", label_visibility="collapsed",
                placeholder=f"Message {partner_name}..."
            )
            sent = col_btn.form_submit_button("Send ➤", use_container_width=True)

            if sent and text.strip():
                send_message(my_email, my_name, partner_email, partner_name, text.strip())
                st.rerun()
