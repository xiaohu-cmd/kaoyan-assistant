"""
Comprehensive integration tests for 考研助手 API.
Run: cd kaoyan-assistant && python -m pytest tests/ -v
"""
import random
import string
import pytest
from fastapi.testclient import TestClient
from backend.main import app


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------
class TestAuth:
    def test_register(self, client):
        # Generate a unique username to avoid collision with existing data
        suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
        username = f"newuser_{suffix}"
        resp = client.post("/api/auth/register", json={"username": username, "password": "pass1234"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == username
        assert "id" in data

    def test_register_duplicate(self, client):
        # Register the integration_test user first, then try again
        client.post("/api/auth/register", json={"username": "dup_test", "password": "testpass"})
        resp = client.post("/api/auth/register", json={"username": "dup_test", "password": "testpass"})
        assert resp.status_code == 400

    def test_login(self, client, auth_headers):
        # auth_headers fixture already registers and logs in, so we just verify the token works
        resp = client.get("/api/dashboard/overview", headers=auth_headers)
        assert resp.status_code == 200

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={"username": "wrongpw_test", "password": "correct"})
        resp = client.post("/api/auth/login", data={"username": "wrongpw_test", "password": "wrong"})
        assert resp.status_code == 401

    def test_protected_route_no_token(self, client):
        resp = client.get("/api/dashboard/overview")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Dashboard tests
# ---------------------------------------------------------------------------
class TestDashboard:
    def test_overview(self, client, auth_headers):
        resp = client.get("/api/dashboard/overview", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "countdown_days" in data
        assert "streak_days" in data
        assert "today_minutes" in data
        assert "subject_progress" in data
        assert len(data["subject_progress"]) >= 4

    def test_heatmap(self, client, auth_headers):
        resp = client.get("/api/dashboard/heatmap?year=2026&month=7", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_weekly_report(self, client, auth_headers):
        resp = client.get("/api/dashboard/weekly-report?date=2026-07-18", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "week_start" in data
        assert "daily_breakdown" in data
        assert len(data["daily_breakdown"]) == 7

    def test_monthly_report(self, client, auth_headers):
        resp = client.get("/api/dashboard/monthly-report?month=2026-07", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "daily_breakdown" in data


# ---------------------------------------------------------------------------
# Tasks tests
# ---------------------------------------------------------------------------
class TestTasks:
    def test_create_task(self, client, auth_headers):
        resp = client.post("/api/tasks", json={
            "title": "Test Task", "subject_id": 1, "phase": "foundation", "priority": 2
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Test Task"

    def test_list_tasks(self, client, auth_headers):
        resp = client.get("/api/tasks", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_update_task_status(self, client, auth_headers):
        tasks = client.get("/api/tasks", headers=auth_headers).json()
        if tasks:
            task_id = tasks[0]["id"]
            resp = client.patch(f"/api/tasks/{task_id}/status", json={"status": "done"}, headers=auth_headers)
            assert resp.status_code == 200
            assert resp.json()["status"] == "done"

    def test_delete_task(self, client, auth_headers):
        resp = client.post("/api/tasks", json={"title": "Delete Me"}, headers=auth_headers)
        assert resp.status_code == 200
        task_id = resp.json()["id"]
        resp = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
        assert resp.status_code == 200

    def test_reorder_tasks(self, client, auth_headers):
        resp = client.patch("/api/tasks/reorder", json=[{"id": 1, "sort_order": 0}], headers=auth_headers)
        assert resp.status_code == 200

    def test_calendar(self, client, auth_headers):
        resp = client.get("/api/tasks/calendar?start=2026-01-01&end=2026-12-31", headers=auth_headers)
        assert resp.status_code == 200

    def test_review_due(self, client, auth_headers):
        resp = client.get("/api/tasks/review-due", headers=auth_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Pomodoro tests
# ---------------------------------------------------------------------------
class TestPomodoro:
    def test_full_cycle(self, client, auth_headers):
        resp = client.post("/api/pomodoro/start", json={"subject_id": 1}, headers=auth_headers)
        assert resp.status_code == 200
        session_id = resp.json()["id"]
        resp = client.post("/api/pomodoro/stop", json={"id": session_id, "duration_seconds": 1500}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["duration_seconds"] == 1500

    def test_today(self, client, auth_headers):
        resp = client.get("/api/pomodoro/today", headers=auth_headers)
        assert resp.status_code == 200
        assert "sessions" in resp.json()

    def test_stats(self, client, auth_headers):
        resp = client.get("/api/pomodoro/stats?start=2026-07-01&end=2026-07-31", headers=auth_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Checkins tests
# ---------------------------------------------------------------------------
class TestCheckins:
    def test_create(self, client, auth_headers):
        resp = client.post("/api/checkins", json={
            "review_text": "Test review", "mood": "good", "tomorrow_plan": "Test plan"
        }, headers=auth_headers)
        assert resp.status_code == 200

    def test_today(self, client, auth_headers):
        resp = client.get("/api/checkins/today", headers=auth_headers)
        assert resp.status_code == 200
        assert "date" in resp.json()

    def test_range(self, client, auth_headers):
        resp = client.get("/api/checkins?start=2026-07-01&end=2026-07-31", headers=auth_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Notes tests
# ---------------------------------------------------------------------------
class TestNotes:
    def test_crud(self, client, auth_headers):
        # Create
        resp = client.post("/api/notes", json={
            "type": "note", "title": "Test Note", "subject_id": 1
        }, headers=auth_headers)
        assert resp.status_code == 200
        note_id = resp.json()["id"]

        # List
        resp = client.get("/api/notes?type=note", headers=auth_headers)
        assert resp.status_code == 200
        assert any(n["id"] == note_id for n in resp.json())

        # Update
        resp = client.put(f"/api/notes/{note_id}", json={"title": "Updated Note"}, headers=auth_headers)
        assert resp.status_code == 200

        # Delete
        resp = client.delete(f"/api/notes/{note_id}", headers=auth_headers)
        assert resp.status_code == 200

    def test_wrong_question(self, client, auth_headers):
        resp = client.post("/api/notes", json={
            "type": "wrong_question", "title": "Wrong Q"
        }, headers=auth_headers)
        note_id = resp.json()["id"]

        resp = client.patch(f"/api/notes/{note_id}/wrong", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["wrong_count"] == 1


# ---------------------------------------------------------------------------
# Materials tests
# ---------------------------------------------------------------------------
class TestMaterials:
    def test_crud(self, client, auth_headers):
        # Create
        resp = client.post("/api/materials", json={
            "title": "Test Book", "type": "book"
        }, headers=auth_headers)
        assert resp.status_code == 200
        mat_id = resp.json()["id"]

        # Update progress
        resp = client.patch(f"/api/materials/{mat_id}/progress", json={
            "reading_progress": 75
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["reading_progress"] == 75

        # Delete
        resp = client.delete(f"/api/materials/{mat_id}", headers=auth_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Flashcards tests
# ---------------------------------------------------------------------------
class TestFlashcards:
    def test_crud_and_review(self, client, auth_headers):
        # Create
        resp = client.post("/api/flashcards", json={
            "front_text": "Q?", "back_text": "A!"
        }, headers=auth_headers)
        assert resp.status_code == 200
        card_id = resp.json()["id"]

        # Review
        resp = client.post(f"/api/flashcards/{card_id}/review", json={
            "feedback": "remembered"
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["review_count"] == 1

        # List
        resp = client.get("/api/flashcards", headers=auth_headers)
        assert resp.status_code == 200

        # Delete
        resp = client.delete(f"/api/flashcards/{card_id}", headers=auth_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Vocab tests
# ---------------------------------------------------------------------------
class TestVocab:
    def test_list(self, client, auth_headers):
        resp = client.get("/api/vocab?limit=5", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data

    def test_review(self, client, auth_headers):
        words = client.get("/api/vocab?limit=1", headers=auth_headers).json()
        if words["items"]:
            word_id = words["items"][0]["id"]
            resp = client.post(f"/api/vocab/{word_id}/review", json={
                "feedback": "remembered"
            }, headers=auth_headers)
            assert resp.status_code == 200

    def test_custom_word(self, client, auth_headers):
        random_word = "zzz" + ''.join(random.choices(string.ascii_lowercase, k=6))
        resp = client.post("/api/vocab/custom", json={
            "word": random_word, "meaning": "test"
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["is_custom"] == 1


# ---------------------------------------------------------------------------
# Reading tests
# ---------------------------------------------------------------------------
class TestReading:
    def test_crud(self, client, auth_headers):
        # Create reading record
        resp = client.post("/api/reading", json={
            "year": 2020, "passage_no": 1, "type": "reading",
            "total_questions": 5, "wrong_count": 2
        }, headers=auth_headers)
        assert resp.status_code == 200
        rec_id = resp.json()["id"]

        # Add a sentence
        resp = client.post(f"/api/reading/{rec_id}/sentences", json={
            "sentence_text": "A test sentence."
        }, headers=auth_headers)
        assert resp.status_code == 200
        sent_id = resp.json()["id"]

        # List sentences
        resp = client.get(f"/api/reading/{rec_id}/sentences", headers=auth_headers)
        assert len(resp.json()) > 0

        # Delete sentence
        resp = client.delete(f"/api/reading/sentences/{sent_id}", headers=auth_headers)
        assert resp.status_code == 200

        # Delete reading record
        resp = client.delete(f"/api/reading/{rec_id}", headers=auth_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Writing tests
# ---------------------------------------------------------------------------
class TestWriting:
    def test_crud(self, client, auth_headers):
        # Create essay
        resp = client.post("/api/writing", json={
            "type": "small", "title": "Test Essay",
            "content": "This is a test essay content with enough words for the AI system."
        }, headers=auth_headers)
        assert resp.status_code == 200
        essay_id = resp.json()["id"]

        # Request AI feedback (works without API key, returns placeholder data)
        resp = client.post(f"/api/writing/{essay_id}/ai-feedback", headers=auth_headers)
        assert resp.status_code == 200

        # Delete
        resp = client.delete(f"/api/writing/{essay_id}", headers=auth_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Schools tests
# ---------------------------------------------------------------------------
class TestSchools:
    def test_crud(self, client, auth_headers):
        # Create
        resp = client.post("/api/schools", json={
            "school_name": "Test University", "year": 2026, "major": "Test Major",
            "admission_line": 380.0, "enrollment_count": 20, "applicant_count": 150
        }, headers=auth_headers)
        assert resp.status_code == 200
        school_id = resp.json()["id"]

        # List
        resp = client.get("/api/schools?year=2026", headers=auth_headers)
        assert any(s["id"] == school_id for s in resp.json())

        # Delete
        resp = client.delete(f"/api/schools/{school_id}", headers=auth_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Settings / Data Export-Import tests
# ---------------------------------------------------------------------------
class TestSettings:
    def test_get_settings(self, client, auth_headers):
        resp = client.get("/api/settings", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "target_school" in data
        assert "exam_date" in data
        assert "pomodoro_focus_minutes" in data

    def test_update_settings(self, client, auth_headers):
        resp = client.put("/api/settings", json={
            "target_school": "厦门大学",
            "pomodoro_focus_minutes": 30
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["target_school"] == "厦门大学"
        assert data["pomodoro_focus_minutes"] == 30

    def test_export_import_roundtrip(self, client, auth_headers):
        # Export
        resp = client.post("/api/settings/data/export", headers=auth_headers)
        assert resp.status_code == 200
        export_data = resp.json()
        assert "version" in export_data
        assert "subjects" in export_data

        # Import the exported data back
        resp = client.post("/api/settings/data/import", json=export_data, headers=auth_headers)
        assert resp.status_code == 200
        assert "Import complete" in resp.json()["message"]


# ---------------------------------------------------------------------------
# Frontend serving tests
# ---------------------------------------------------------------------------
class TestFrontendServing:
    def test_index_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "login-overlay" in resp.text

    def test_css(self, client):
        resp = client.get("/css/style.css")
        assert resp.status_code == 200
        assert "--bg" in resp.text

    def test_js_files(self, client):
        js_files = [
            "/js/api.js", "/js/app.js",
            "/js/pages/dashboard.js", "/js/pages/plan.js",
            "/js/pages/english.js", "/js/pages/resources.js",
            "/js/pages/schools.js", "/js/pages/settings.js",
        ]
        for path in js_files:
            resp = client.get(path)
            assert resp.status_code == 200, f"{path} should return 200"
