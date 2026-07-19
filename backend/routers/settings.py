import json
import os
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import get_db, DATABASE_PATH
from backend.routers.auth import get_current_user
import sqlite3

router = APIRouter(prefix="/api/settings", tags=["settings"])

SETTINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
SETTINGS_PATH = os.path.join(SETTINGS_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "target_school": "",
    "exam_date": "2027-12-25",
    "foundation_start": "2026-07-01",
    "foundation_end": "2027-03-31",
    "intensive_start": "2027-04-01",
    "intensive_end": "2027-08-31",
    "sprint_start": "2027-09-01",
    "sprint_end": "2027-12-20",
    "daily_new_words": 50,
    "daily_task_count": 5,
    "pomodoro_focus_minutes": 25,
    "pomodoro_short_break_minutes": 5,
    "pomodoro_long_break_minutes": 15,
    "pomodoro_sessions_before_long_break": 4,
    "ai_api_key": "",
    "ai_api_base": "https://api.openai.com/v1",
    "ai_model": "gpt-3.5-turbo",
    "username": "admin",
}


def load_settings() -> dict:
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    if not os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False, indent=2)
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(data: dict) -> None:
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class SettingsUpdate(BaseModel):
    target_school: Optional[str] = None
    exam_date: Optional[str] = None
    foundation_start: Optional[str] = None
    foundation_end: Optional[str] = None
    intensive_start: Optional[str] = None
    intensive_end: Optional[str] = None
    sprint_start: Optional[str] = None
    sprint_end: Optional[str] = None
    daily_new_words: int = 30
    daily_task_count: Optional[int] = None
    pomodoro_focus_minutes: Optional[int] = None
    pomodoro_short_break_minutes: Optional[int] = None
    pomodoro_long_break_minutes: Optional[int] = None
    pomodoro_sessions_before_long_break: Optional[int] = None
    ai_api_key: Optional[str] = None
    ai_api_base: Optional[str] = None
    ai_model: Optional[str] = None
    username: Optional[str] = None


@router.get("")
def get_settings(
    current_user: dict = Depends(get_current_user)
):
    return load_settings()


@router.put("")
def update_settings(
    settings: SettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    current = load_settings()
    for field, value in settings.model_dump(exclude_unset=True).items():
        if value is not None:
            current[field] = value
    save_settings(current)
    return current


@router.post("/data/export")
def export_data(
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    data = {}
    tables = ["subjects", "tasks", "pomodoro_sessions", "daily_checkins",
              "notes_and_errors", "materials", "flashcards", "vocab_words",
              "reading_records", "reading_sentences", "writing_essays", "school_info"]
    for table in tables:
        rows = db.execute(f"SELECT * FROM {table}").fetchall()
        data[table] = [dict(r) for r in rows]
    data["settings"] = load_settings()
    data["exported_at"] = datetime.now().isoformat()
    data["version"] = "1.0"
    return data


@router.post("/data/import")
async def import_data(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    if "version" not in request:
        raise HTTPException(status_code=400, detail="Invalid import format: missing version field")
    tables = ["subjects", "tasks", "pomodoro_sessions", "daily_checkins",
              "notes_and_errors", "materials", "flashcards", "vocab_words",
              "reading_records", "reading_sentences", "writing_essays", "school_info"]
    # Use direct connection to avoid sqlite3 thread-safety issues in async endpoints
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        imported_count = 0
        for table in tables:
            if table in request:
                rows = request[table]
                for row in rows:
                    row_copy = {k: v for k, v in row.items() if k != "id"}
                    if not row_copy:
                        continue
                    columns = ", ".join(row_copy.keys())
                    placeholders = ", ".join("?" for _ in row_copy)
                    conn.execute(
                        f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})",
                        list(row_copy.values())
                    )
                    imported_count += 1
        conn.commit()
        if "settings" in request:
            save_settings(request["settings"])
        return {"message": f"Import complete. {imported_count} rows imported.", "imported": imported_count}
    finally:
        conn.close()
