"""
Pytest fixtures for 考研助手 integration tests.
"""
import pytest
import sqlite3
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import DATABASE_PATH, DATABASE_DIR, init_db
import os


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Ensure database exists and has seed subjects."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    init_db()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO subjects (name, color, icon, sort_order) VALUES (?, ?, ?, ?)",
            [
                ("政治", "#ef4444", "flag", 1),
                ("英语二", "#f59e0b", "translate", 2),
                ("数学三", "#3b82f6", "function", 3),
                ("432统计学", "#22c55e", "bar-chart", 4),
            ]
        )
        conn.commit()
    conn.close()


@pytest.fixture
def client():
    """FastAPI TestClient wrapping the app."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register a test user and return auth headers.
    Gracefully handles the case where the user already exists from a previous run.
    """
    username = "integration_test"
    password = "testpass"

    # Try to register; ignore duplicate (400) if user already exists
    resp = client.post("/api/auth/register", json={"username": username, "password": password})
    # Only raise if it's not a duplicate error
    if resp.status_code not in (200, 400):
        resp.raise_for_status()

    # Login to get token
    resp = client.post("/api/auth/login", data={"username": username, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
