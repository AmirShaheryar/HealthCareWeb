from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import os

# Defaults to the same location as before (next to app.py).
# In production, set MEDORA_DB_PATH to a persistent-volume path
# (e.g. /data/medora.db on Fly.io) so data survives redeploys/restarts.
DB_PATH = Path(os.environ.get(
    "MEDORA_DB_PATH",
    str(Path(__file__).resolve().parent.parent / "medora.db"),
))

DEMO_USERS: dict[str, dict[str, Any]] = {
    "patient@demo.com": {"password": "patient123", "role": "User",   "name": "Ali Raza",    "verified": True},
    "doctor@demo.com":  {"password": "doctor123",  "role": "Doctor", "name": "Dr. Sara Khan","verified": True},
    "admin@demo.com":   {"password": "admin123",   "role": "Admin",  "name": "Admin User",  "verified": True},
}


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_user_db() -> None:
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                data  TEXT NOT NULL
            )
            """
        )
        conn.commit()


def load_users_db() -> dict[str, dict[str, Any]]:
    init_user_db()
    users: dict[str, dict[str, Any]] = {}
    with _conn() as conn:
        rows = conn.execute("SELECT email, data FROM users").fetchall()
    for email, data_str in rows:
        try:
            users[email] = json.loads(data_str)
        except json.JSONDecodeError:
            continue
    return users


def upsert_user(email: str, data: dict[str, Any]) -> None:
    payload = json.dumps(data)
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO users(email, data)
            VALUES (?, ?)
            ON CONFLICT(email) DO UPDATE SET data=excluded.data
            """,
            (email, payload),
        )
        conn.commit()


def delete_user(email: str) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()


def seed_demo_users_if_empty() -> dict[str, dict[str, Any]]:
    users = load_users_db()
    if users:
        return users
    for email, data in DEMO_USERS.items():
        upsert_user(email, data)
    return load_users_db()


def init_notes_db() -> None:
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clinical_notes (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                email     TEXT NOT NULL,
                patient   TEXT NOT NULL,
                type      TEXT NOT NULL,
                content   TEXT NOT NULL,
                doctor    TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.commit()


def add_clinical_note(note: dict[str, Any]) -> None:
    init_notes_db()
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO clinical_notes(email, patient, type, content, doctor, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                note.get("email", ""),
                note.get("patient", ""),
                note.get("type", "General"),
                note.get("content", ""),
                note.get("doctor", ""),
                note.get("timestamp", ""),
            ),
        )
        conn.commit()


def get_verified_doctors(users: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Return verified doctors sorted by name for patient selection."""
    doctors: list[dict[str, Any]] = []
    for email, data in users.items():
        if data.get("role") == "Doctor" and data.get("verified", False):
            doctors.append({
                "email": email,
                "name": data.get("name", email),
                "specialty": data.get("specialty", "General Physician"),
                "hospital": data.get("hospital", ""),
            })
    return sorted(doctors, key=lambda d: d["name"].lower())


def get_clinical_notes_for_email(email: str) -> list[dict[str, Any]]:
    init_notes_db()
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT email, patient, type, content, doctor, timestamp
            FROM clinical_notes
            WHERE email = ?
            ORDER BY id DESC
            """,
            (email,),
        ).fetchall()
    return [
        {"email": r[0], "patient": r[1], "type": r[2], "content": r[3], "doctor": r[4], "timestamp": r[5]}
        for r in rows
    ]


# ── Patient <-> Doctor Chat Messages ──────────────────────────────────────────

def init_messages_db() -> None:
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_email   TEXT NOT NULL,
                receiver_email TEXT NOT NULL,
                sender_name    TEXT NOT NULL,
                receiver_name  TEXT NOT NULL,
                content        TEXT NOT NULL,
                timestamp      TEXT NOT NULL,
                is_read        INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_pair
            ON messages(sender_email, receiver_email)
            """
        )
        conn.commit()


def send_message(sender_email: str, sender_name: str,
                  receiver_email: str, receiver_name: str,
                  content: str) -> None:
    init_messages_db()
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO messages(sender_email, receiver_email, sender_name,
                                  receiver_name, content, timestamp, is_read)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (
                sender_email, receiver_email, sender_name, receiver_name,
                content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()


def get_conversation(email_a: str, email_b: str) -> list[dict[str, Any]]:
    """All messages between two people, oldest first."""
    init_messages_db()
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT sender_email, receiver_email, sender_name, receiver_name,
                   content, timestamp, is_read, id
            FROM messages
            WHERE (sender_email = ? AND receiver_email = ?)
               OR (sender_email = ? AND receiver_email = ?)
            ORDER BY id ASC
            """,
            (email_a, email_b, email_b, email_a),
        ).fetchall()
    return [
        {
            "sender_email": r[0], "receiver_email": r[1],
            "sender_name": r[2], "receiver_name": r[3],
            "content": r[4], "timestamp": r[5], "is_read": bool(r[6]), "id": r[7],
        }
        for r in rows
    ]


def mark_conversation_read(owner_email: str, other_email: str) -> None:
    """Mark messages sent TO owner_email FROM other_email as read."""
    init_messages_db()
    with _conn() as conn:
        conn.execute(
            """
            UPDATE messages SET is_read = 1
            WHERE receiver_email = ? AND sender_email = ? AND is_read = 0
            """,
            (owner_email, other_email),
        )
        conn.commit()


def get_conversations_for_user(email: str) -> list[dict[str, Any]]:
    """
    One row per conversation partner for `email`, with last-message preview
    and unread count, most recently active first.
    """
    init_messages_db()
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT sender_email, receiver_email, sender_name, receiver_name,
                   content, timestamp, is_read
            FROM messages
            WHERE sender_email = ? OR receiver_email = ?
            ORDER BY id ASC
            """,
            (email, email),
        ).fetchall()

    convos: dict[str, dict[str, Any]] = {}
    for sender_email, receiver_email, sender_name, receiver_name, content, ts, is_read in rows:
        other_email = receiver_email if sender_email == email else sender_email
        other_name  = receiver_name if sender_email == email else sender_name
        convo = convos.setdefault(other_email, {
            "email": other_email, "name": other_name,
            "last_message": "", "last_timestamp": "", "unread": 0,
        })
        convo["name"] = other_name
        convo["last_message"] = content
        convo["last_timestamp"] = ts
        if receiver_email == email and not is_read:
            convo["unread"] += 1

    return sorted(convos.values(), key=lambda c: c["last_timestamp"], reverse=True)


def get_unread_message_count(email: str) -> int:
    init_messages_db()
    with _conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE receiver_email = ? AND is_read = 0",
            (email,),
        ).fetchone()
    return row[0] if row else 0


def get_all_patients(users: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """All patients (role == 'User'), sorted by name, for doctor-side selection."""
    patients: list[dict[str, Any]] = []
    for email, data in users.items():
        if data.get("role") == "User":
            patients.append({"email": email, "name": data.get("name", email)})
    return sorted(patients, key=lambda p: p["name"].lower())


# ── Appointment Booking ────────────────────────────────────────────────────────

def init_appointments_db() -> None:
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor_slots (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_email TEXT NOT NULL,
                doctor_name  TEXT NOT NULL,
                slot_date    TEXT NOT NULL,   -- YYYY-MM-DD
                slot_time    TEXT NOT NULL,   -- HH:MM (24h)
                status       TEXT NOT NULL DEFAULT 'Open'   -- Open, Booked, Removed
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_id       INTEGER NOT NULL,
                patient_email TEXT NOT NULL,
                patient_name  TEXT NOT NULL,
                doctor_email  TEXT NOT NULL,
                doctor_name   TEXT NOT NULL,
                slot_date     TEXT NOT NULL,
                slot_time     TEXT NOT NULL,
                reason        TEXT,
                status        TEXT NOT NULL DEFAULT 'Confirmed',  -- Confirmed, Completed, Cancelled
                created_at    TEXT NOT NULL
            )
            """
        )
        conn.commit()


def add_doctor_slot(doctor_email: str, doctor_name: str, slot_date: str, slot_time: str) -> None:
    init_appointments_db()
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO doctor_slots(doctor_email, doctor_name, slot_date, slot_time, status)
            VALUES (?, ?, ?, ?, 'Open')
            """,
            (doctor_email, doctor_name, slot_date, slot_time),
        )
        conn.commit()


def remove_doctor_slot(slot_id: int) -> None:
    """Only removes a slot if it hasn't been booked yet."""
    init_appointments_db()
    with _conn() as conn:
        conn.execute(
            "UPDATE doctor_slots SET status = 'Removed' WHERE id = ? AND status = 'Open'",
            (slot_id,),
        )
        conn.commit()


def get_open_slots_for_doctor(doctor_email: str) -> list[dict[str, Any]]:
    init_appointments_db()
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT id, doctor_email, doctor_name, slot_date, slot_time, status
            FROM doctor_slots
            WHERE doctor_email = ? AND status = 'Open'
            ORDER BY slot_date ASC, slot_time ASC
            """,
            (doctor_email,),
        ).fetchall()
    return [
        {"id": r[0], "doctor_email": r[1], "doctor_name": r[2],
         "slot_date": r[3], "slot_time": r[4], "status": r[5]}
        for r in rows
    ]


def get_all_slots_for_doctor(doctor_email: str) -> list[dict[str, Any]]:
    """All slots (any status) for a doctor's own management view."""
    init_appointments_db()
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT id, doctor_email, doctor_name, slot_date, slot_time, status
            FROM doctor_slots
            WHERE doctor_email = ?
            ORDER BY slot_date ASC, slot_time ASC
            """,
            (doctor_email,),
        ).fetchall()
    return [
        {"id": r[0], "doctor_email": r[1], "doctor_name": r[2],
         "slot_date": r[3], "slot_time": r[4], "status": r[5]}
        for r in rows
    ]


def book_slot(slot_id: int, patient_email: str, patient_name: str, reason: str) -> bool:
    """
    Book an open slot for a patient. Returns True on success, False if the
    slot was no longer open (e.g. someone else booked it first).
    """
    init_appointments_db()
    with _conn() as conn:
        row = conn.execute(
            "SELECT doctor_email, doctor_name, slot_date, slot_time, status FROM doctor_slots WHERE id = ?",
            (slot_id,),
        ).fetchone()
        if not row or row[4] != "Open":
            return False

        doctor_email, doctor_name, slot_date, slot_time, _ = row
        conn.execute("UPDATE doctor_slots SET status = 'Booked' WHERE id = ?", (slot_id,))
        conn.execute(
            """
            INSERT INTO appointments(slot_id, patient_email, patient_name, doctor_email,
                                      doctor_name, slot_date, slot_time, reason, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?)
            """,
            (
                slot_id, patient_email, patient_name, doctor_email, doctor_name,
                slot_date, slot_time, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
    return True


def get_appointments_for_patient(patient_email: str) -> list[dict[str, Any]]:
    init_appointments_db()
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT id, slot_id, patient_email, patient_name, doctor_email, doctor_name,
                   slot_date, slot_time, reason, status, created_at
            FROM appointments
            WHERE patient_email = ?
            ORDER BY slot_date ASC, slot_time ASC
            """,
            (patient_email,),
        ).fetchall()
    return _rows_to_appointments(rows)


def get_appointments_for_doctor(doctor_email: str) -> list[dict[str, Any]]:
    init_appointments_db()
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT id, slot_id, patient_email, patient_name, doctor_email, doctor_name,
                   slot_date, slot_time, reason, status, created_at
            FROM appointments
            WHERE doctor_email = ?
            ORDER BY slot_date ASC, slot_time ASC
            """,
            (doctor_email,),
        ).fetchall()
    return _rows_to_appointments(rows)


def _rows_to_appointments(rows) -> list[dict[str, Any]]:
    return [
        {
            "id": r[0], "slot_id": r[1], "patient_email": r[2], "patient_name": r[3],
            "doctor_email": r[4], "doctor_name": r[5], "slot_date": r[6], "slot_time": r[7],
            "reason": r[8], "status": r[9], "created_at": r[10],
        }
        for r in rows
    ]


def cancel_appointment(appointment_id: int) -> None:
    """Cancel an appointment and free its slot back up for others to book."""
    init_appointments_db()
    with _conn() as conn:
        row = conn.execute(
            "SELECT slot_id FROM appointments WHERE id = ?", (appointment_id,)
        ).fetchone()
        conn.execute(
            "UPDATE appointments SET status = 'Cancelled' WHERE id = ?", (appointment_id,)
        )
        if row:
            conn.execute(
                "UPDATE doctor_slots SET status = 'Open' WHERE id = ? AND status = 'Booked'",
                (row[0],),
            )
        conn.commit()


def mark_appointment_completed(appointment_id: int) -> None:
    init_appointments_db()
    with _conn() as conn:
        conn.execute(
            "UPDATE appointments SET status = 'Completed' WHERE id = ?", (appointment_id,)
        )
        conn.commit()


def get_upcoming_appointment_count(email: str, role: str) -> int:
    """Count of Confirmed appointments today or later, for sidebar badges."""
    init_appointments_db()
    today = datetime.now().strftime("%Y-%m-%d")
    col = "patient_email" if role == "User" else "doctor_email"
    with _conn() as conn:
        row = conn.execute(
            f"""
            SELECT COUNT(*) FROM appointments
            WHERE {col} = ? AND status = 'Confirmed' AND slot_date >= ?
            """,
            (email, today),
        ).fetchone()
    return row[0] if row else 0
