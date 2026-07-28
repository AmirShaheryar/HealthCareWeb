import streamlit as st
from datetime import datetime, date, time
from modules.db import (
    add_doctor_slot,
    remove_doctor_slot,
    get_open_slots_for_doctor,
    get_all_slots_for_doctor,
    book_slot,
    get_appointments_for_patient,
    get_appointments_for_doctor,
    cancel_appointment,
    mark_appointment_completed,
    get_verified_doctors,
)

STATUS_COLORS = {
    "Confirmed": "alert-blue",
    "Completed": "alert-green",
    "Cancelled": "alert-red",
}


def show():
    my_email = st.session_state.get("user_email", "")
    my_name  = st.session_state.get("username", "")
    my_role  = st.session_state.get("user_role", "")

    if my_role not in ("User", "Doctor"):
        st.warning("🚫 Appointment booking is available for patients and doctors only.")
        return

    st.markdown('<p class="section-title">📅 Appointments</p>', unsafe_allow_html=True)

    if my_role == "Doctor":
        _doctor_view(my_email, my_name)
    else:
        _patient_view(my_email, my_name)


# ══════════════════════════════════════════════════════════════════════════
# DOCTOR VIEW
# ══════════════════════════════════════════════════════════════════════════
def _doctor_view(my_email: str, my_name: str):
    st.caption("Publish open time slots for patients to book, and manage your upcoming visits.")

    tab_slots, tab_appts = st.tabs(["🗓️ My Availability", "📋 My Appointments"])

    # ── Manage availability ──────────────────────────────────
    with tab_slots:
        with st.form("add_slot_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            slot_date = col1.date_input("Date", min_value=date.today())
            slot_time = col2.time_input("Time", value=time(9, 0), step=900)  # 15-min steps

            if st.form_submit_button("➕ Add Slot", use_container_width=True):
                add_doctor_slot(
                    my_email, my_name,
                    slot_date.strftime("%Y-%m-%d"),
                    slot_time.strftime("%H:%M"),
                )
                st.success(f"✅ Slot added: {slot_date.strftime('%d %b %Y')} at {slot_time.strftime('%H:%M')}")
                st.rerun()

        st.divider()
        st.markdown("#### Your Slots")
        slots = get_all_slots_for_doctor(my_email)
        if not slots:
            st.info("No slots created yet. Add one above so patients can book you.")
        else:
            for s in slots:
                badge = {"Open": "🟢", "Booked": "🔵", "Removed": "⚪"}.get(s["status"], "")
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"{badge} **{s['slot_date']}** at **{s['slot_time']}** — {s['status']}")
                if s["status"] == "Open":
                    if col_b.button("🗑️ Remove", key=f"rm_slot_{s['id']}"):
                        remove_doctor_slot(s["id"])
                        st.rerun()

    # ── Appointments ────────────────────────────────────────────
    with tab_appts:
        appts = get_appointments_for_doctor(my_email)
        upcoming = [a for a in appts if a["status"] == "Confirmed"]
        past     = [a for a in appts if a["status"] in ("Completed", "Cancelled")]

        c1, c2, c3 = st.columns(3)
        c1.metric("📅 Upcoming", len(upcoming))
        c2.metric("✅ Completed", len([a for a in past if a["status"] == "Completed"]))
        c3.metric("❌ Cancelled", len([a for a in past if a["status"] == "Cancelled"]))

        st.markdown("#### Upcoming")
        if not upcoming:
            st.info("No upcoming appointments.")
        for a in upcoming:
            with st.expander(f"{a['slot_date']} {a['slot_time']} — {a['patient_name']}"):
                st.write(f"**Patient:** {a['patient_name']} ({a['patient_email']})")
                st.write(f"**Reason:** {a.get('reason') or '—'}")
                col_a, col_b = st.columns(2)
                if col_a.button("✅ Mark Completed", key=f"done_{a['id']}"):
                    mark_appointment_completed(a["id"])
                    st.rerun()
                if col_b.button("❌ Cancel", key=f"cancel_doc_{a['id']}"):
                    cancel_appointment(a["id"])
                    st.rerun()

        st.markdown("#### History")
        if not past:
            st.caption("No past appointments yet.")
        for a in sorted(past, key=lambda x: x["slot_date"], reverse=True):
            css = STATUS_COLORS.get(a["status"], "alert-blue")
            st.markdown(
                f"""<div class="{css}">
                    <b>{a['slot_date']} {a['slot_time']}</b> — {a['patient_name']} — {a['status']}<br>
                    <small>{a.get('reason') or ''}</small>
                </div>""",
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════
# PATIENT VIEW
# ══════════════════════════════════════════════════════════════════════════
def _patient_view(my_email: str, my_name: str):
    st.caption("Book a time with a verified doctor, or manage your existing appointments.")

    tab_book, tab_mine = st.tabs(["🔎 Book a Doctor", "📋 My Appointments"])

    # ── Book a new appointment ──────────────────────────────
    with tab_book:
        doctors = get_verified_doctors(st.session_state.users_db)
        if not doctors:
            st.info("No verified doctors available yet.")
        else:
            doc_labels = [f"{d['name']} — {d.get('specialty','General Physician')}" for d in doctors]
            chosen = st.selectbox("Choose a doctor", doc_labels)
            doctor = doctors[doc_labels.index(chosen)]

            open_slots = get_open_slots_for_doctor(doctor["email"])
            if not open_slots:
                st.warning(f"😕 {doctor['name']} has no open slots right now. Please check back later.")
            else:
                slot_labels = [f"{s['slot_date']} at {s['slot_time']}" for s in open_slots]
                slot_choice = st.selectbox("Available slots", slot_labels)
                chosen_slot = open_slots[slot_labels.index(slot_choice)]

                reason = st.text_area("Reason for visit (optional)", placeholder="e.g. Follow-up on blood test results")

                if st.button("📅 Book Appointment", use_container_width=True):
                    ok = book_slot(chosen_slot["id"], my_email, my_name, reason.strip())
                    if ok:
                        st.success(f"✅ Appointment booked with {doctor['name']} on {chosen_slot['slot_date']} at {chosen_slot['slot_time']}!")
                        st.rerun()
                    else:
                        st.error("❌ Sorry, that slot was just booked by someone else. Please pick another.")
                        st.rerun()

    # ── My appointments ──────────────────────────────────────
    with tab_mine:
        appts = get_appointments_for_patient(my_email)
        upcoming = [a for a in appts if a["status"] == "Confirmed"]
        past     = [a for a in appts if a["status"] in ("Completed", "Cancelled")]

        st.markdown("#### Upcoming")
        if not upcoming:
            st.info("You have no upcoming appointments.")
        for a in upcoming:
            with st.expander(f"{a['slot_date']} {a['slot_time']} — Dr. {a['doctor_name']}"):
                st.write(f"**Doctor:** {a['doctor_name']}")
                st.write(f"**Reason:** {a.get('reason') or '—'}")
                if st.button("❌ Cancel Appointment", key=f"cancel_pat_{a['id']}"):
                    cancel_appointment(a["id"])
                    st.success("Appointment cancelled.")
                    st.rerun()

        st.markdown("#### History")
        if not past:
            st.caption("No past appointments yet.")
        for a in sorted(past, key=lambda x: x["slot_date"], reverse=True):
            css = STATUS_COLORS.get(a["status"], "alert-blue")
            st.markdown(
                f"""<div class="{css}">
                    <b>{a['slot_date']} {a['slot_time']}</b> — Dr. {a['doctor_name']} — {a['status']}<br>
                    <small>{a.get('reason') or ''}</small>
                </div>""",
                unsafe_allow_html=True,
            )
