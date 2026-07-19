from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import get_db
from backend.routers.auth import get_current_user
import sqlite3

router = APIRouter(prefix="/api/checkins", tags=["checkins"])


class CheckinCreate(BaseModel):
    review_text: str = ""
    mood: str = "neutral"
    tomorrow_plan: str = ""


class CheckinUpdate(BaseModel):
    review_text: Optional[str] = None
    mood: Optional[str] = None
    tomorrow_plan: Optional[str] = None


@router.post("")
def create_checkin(
    body: CheckinCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    today = date.today().isoformat()
    now = datetime.now().isoformat()
    total = db.execute(
        "SELECT COALESCE(SUM(duration_seconds), 0) as sec FROM pomodoro_sessions WHERE date(started_at) = ? AND type = 'focus'",
        (today,)
    ).fetchone()
    total_minutes = total["sec"] // 60

    cursor = db.execute(
        "INSERT INTO daily_checkins (date, checkin_time, review_text, mood, tomorrow_plan, total_minutes) VALUES (?, ?, ?, ?, ?, ?)",
        (today, now, body.review_text, body.mood, body.tomorrow_plan, total_minutes)
    )
    row = db.execute("SELECT * FROM daily_checkins WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.put("/{checkin_id}")
def update_checkin(
    checkin_id: int,
    body: CheckinUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT * FROM daily_checkins WHERE id = ?", (checkin_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Checkin not found")
    updates = {k: v for k, v in body.model_dump(exclude_unset=True).items() if v is not None}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [checkin_id]
        db.execute(f"UPDATE daily_checkins SET {set_clause} WHERE id = ?", vals)
    row = db.execute("SELECT * FROM daily_checkins WHERE id = ?", (checkin_id,)).fetchone()
    return dict(row)


@router.delete("/{checkin_id}")
def delete_checkin(
    checkin_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM daily_checkins WHERE id = ?", (checkin_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Checkin not found")
    db.execute("DELETE FROM daily_checkins WHERE id = ?", (checkin_id,))
    return {"message": "Checkin deleted", "id": checkin_id}


@router.get("/today")
def get_today_checkin(
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    today = date.today().isoformat()
    row = db.execute(
        "SELECT * FROM daily_checkins WHERE date = ? ORDER BY checkin_time DESC LIMIT 1",
        (today,)
    ).fetchone()
    if not row:
        total = db.execute(
            "SELECT COALESCE(SUM(duration_seconds), 0) as sec FROM pomodoro_sessions WHERE date(started_at) = ? AND type = 'focus'",
            (today,)
        ).fetchone()
        return {"date": today, "checkin_time": None, "total_minutes": total["sec"] // 60, "review_text": "", "mood": "neutral", "tomorrow_plan": ""}
    return dict(row)


@router.get("")
def get_checkins_range(
    start: str = Query(...),
    end: str = Query(...),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    rows = db.execute(
        "SELECT * FROM daily_checkins WHERE date >= ? AND date <= ? ORDER BY date DESC, checkin_time DESC",
        (start, end)
    ).fetchall()
    return [dict(r) for r in rows]
