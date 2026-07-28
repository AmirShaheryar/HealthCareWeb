"""Tests for ``modules.db`` using an isolated temporary SQLite file."""

import pytest

from modules import db as dbmod


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    db_path = tmp_path / "test_medora.db"
    monkeypatch.setattr(dbmod, "DB_PATH", db_path)
    dbmod.init_user_db()
    yield db_path
    if db_path.exists():
        try:
            db_path.unlink()
        except OSError:
            pass


def test_init_and_upsert_user(isolated_db):
    dbmod.upsert_user("a@test.com", {"password": "x", "role": "User", "name": "A"})
    users = dbmod.load_users_db()
    assert users["a@test.com"]["name"] == "A"


def test_upsert_replaces_user(isolated_db):
    dbmod.upsert_user("b@test.com", {"password": "1", "role": "User"})
    dbmod.upsert_user("b@test.com", {"password": "2", "role": "Doctor"})
    users = dbmod.load_users_db()
    assert users["b@test.com"]["password"] == "2"
    assert users["b@test.com"]["role"] == "Doctor"


def test_load_users_db_skips_bad_json(isolated_db):
    dbmod.init_user_db()
    with dbmod._conn() as conn:
        conn.execute(
            "INSERT INTO users(email, data) VALUES (?, ?)",
            ("bad@test.com", "not-json{"),
        )
        conn.commit()
    users = dbmod.load_users_db()
    assert "bad@test.com" not in users


def test_delete_user(isolated_db):
    dbmod.upsert_user("c@test.com", {"password": "p"})
    dbmod.delete_user("c@test.com")
    assert "c@test.com" not in dbmod.load_users_db()


def test_seed_demo_users_if_empty(isolated_db):
    users = dbmod.seed_demo_users_if_empty()
    assert "patient@demo.com" in users
    assert users["doctor@demo.com"]["role"] == "Doctor"


def test_clinical_notes_roundtrip(isolated_db):
    note = {
        "email": "patient@demo.com",
        "patient": "Ali",
        "type": "SOAP",
        "content": "Rest advised",
        "doctor": "Dr. Test",
        "timestamp": "2026-05-11 10:00",
    }
    dbmod.add_clinical_note(note)
    rows = dbmod.get_clinical_notes_for_email("patient@demo.com")
    assert len(rows) == 1
    assert rows[0]["content"] == "Rest advised"
    assert rows[0]["doctor"] == "Dr. Test"
