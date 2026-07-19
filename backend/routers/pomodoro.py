from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import get_db
from backend.routers.auth import get_current_user
import sqlite3

router = APIRouter(prefix="/api/pomodoro", tags=["pomodoro"])


class PomodoroStart(BaseModel):
    task_id: Optional[int] = None
    subject_id: Optional[int] = None
    type: str = "focus"


class PomodoroStop(BaseModel):
    id: int
    duration_seconds: Optional[int] = None


@router.post("/start")
def start_pomodoro(
    body: PomodoroStart,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    now = datetime.now().isoformat()
    cursor = db.execute(
        "INSERT INTO pomodoro_sessions (task_id, subject_id, type, started_at) VALUES (?, ?, ?, ?)",
        (body.task_id, body.subject_id, body.type, now)
    )
    return {"id": cursor.lastrowid, "started_at": now}


@router.post("/stop")
def stop_pomodoro(
    body: PomodoroStop,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    sess = db.execute("SELECT * FROM pomodoro_sessions WHERE id = ?", (body.id,)).fetchone()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    now = datetime.now().isoformat()
    if body.duration_seconds is not None:
        duration = body.duration_seconds
    else:
        started = datetime.fromisoformat(sess["started_at"])
        duration = int((datetime.now() - started).total_seconds())
    db.execute(
        "UPDATE pomodoro_sessions SET ended_at = ?, duration_seconds = ? WHERE id = ?",
        (now, duration, body.id)
    )
    row = db.execute("SELECT * FROM pomodoro_sessions WHERE id = ?", (body.id,)).fetchone()
    return dict(row)


@router.get("/today")
def get_today(
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    today = date.today().isoformat()
    sessions = db.execute(
        """SELECT p.*, s.name as subject_name, s.color as subject_color
           FROM pomodoro_sessions p
           LEFT JOIN subjects s ON p.subject_id = s.id
           WHERE date(p.started_at) = ?
           ORDER BY p.started_at DESC""",
        (today,)
    ).fetchall()
    total = db.execute(
        "SELECT COALESCE(SUM(duration_seconds), 0) as sec FROM pomodoro_sessions WHERE date(started_at) = ? AND type = 'focus'",
        (today,)
    ).fetchone()
    return {
        "sessions": [dict(s) for s in sessions],
        "total_seconds": total["sec"]
    }


@router.get("/stats")
def get_stats(
    start: str = Query(...),
    end: str = Query(...),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    sessions = db.execute(
        """SELECT p.*, s.name as subject_name, s.color as subject_color
           FROM pomodoro_sessions p
           LEFT JOIN subjects s ON p.subject_id = s.id
           WHERE date(p.started_at) >= ? AND date(p.started_at) <= ?
           ORDER BY p.started_at DESC""",
        (start, end)
    ).fetchall()
    subject_stats = db.execute(
        """SELECT s.id, s.name, s.color, COALESCE(SUM(p.duration_seconds), 0) as total_sec
           FROM subjects s
           LEFT JOIN pomodoro_sessions p ON s.id = p.subject_id AND p.type = 'focus'
               AND date(p.started_at) >= ? AND date(p.started_at) <= ?
           GROUP BY s.id ORDER BY s.sort_order""",
        (start, end)
    ).fetchall()
    return {
        "sessions": [dict(s) for s in sessions],
        "subject_breakdown": [dict(s) for s in subject_stats],
    }
