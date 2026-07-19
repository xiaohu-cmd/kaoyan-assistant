from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Query
from backend.database import get_db, DATABASE_DIR
from backend.routers.auth import get_current_user
import sqlite3, json, os

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

SETTINGS_FILE = os.path.join(DATABASE_DIR, "settings.json")

def _load_exam_date():
    """Load exam date from settings file, fallback to 2027-12-25."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            if settings.get('exam_date'):
                return date.fromisoformat(settings['exam_date'])
    except Exception:
        pass
    return date(2027, 12, 25)


@router.get("/overview")
def get_overview(
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    today = date.today().isoformat()
    exam_date = _load_exam_date()
    countdown_days = (exam_date - date.today()).days

    # Streak: count consecutive days with checkins
    streak = 0
    check_d = date.today()
    while True:
        row = db.execute(
            "SELECT id FROM daily_checkins WHERE date = ?",
            (check_d.isoformat(),)
        ).fetchone()
        if row:
            streak += 1
            check_d -= timedelta(days=1)
        else:
            break

    # Today's study minutes
    today_row = db.execute(
        "SELECT COALESCE(SUM(duration_seconds), 0) as total_sec FROM pomodoro_sessions "
        "WHERE date(started_at) = ? AND type = 'focus'",
        (today,)
    ).fetchone()
    today_minutes = today_row["total_sec"] // 60 if today_row else 0

    # Today's tasks
    today_tasks = db.execute(
        """SELECT t.id, t.title, t.due_date,
                  s.name as subject_name, s.color as subject_color,
                  t.status, t.phase
           FROM tasks t
           LEFT JOIN subjects s ON t.subject_id = s.id
           WHERE t.added_to_today = ?
           ORDER BY t.priority DESC, t.sort_order ASC
           LIMIT 20""",
        (today,)
    ).fetchall()
    today_tasks_count = len(today_tasks)

    # Subject progress: task completion rate + time achievement rate
    subjects = db.execute("SELECT * FROM subjects ORDER BY sort_order").fetchall()
    subject_progress = []
    for subj in subjects:
        # Task completion rate
        total_tasks = db.execute(
            "SELECT COUNT(*) as c FROM tasks WHERE subject_id = ?", (subj["id"],)
        ).fetchone()["c"]
        done_tasks = db.execute(
            "SELECT COUNT(*) as c FROM tasks WHERE subject_id = ? AND status = 'done'",
            (subj["id"],)
        ).fetchone()["c"]
        task_rate = round(done_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0.0

        # Time achievement rate
        actual = db.execute(
            "SELECT COALESCE(SUM(duration_seconds), 0) as sec FROM pomodoro_sessions "
            "WHERE subject_id = ? AND type = 'focus'",
            (subj["id"],)
        ).fetchone()["sec"] // 60
        planned = db.execute(
            "SELECT COALESCE(SUM(estimated_minutes), 0) as m FROM tasks WHERE subject_id = ?",
            (subj["id"],)
        ).fetchone()["m"]
        time_rate = round(actual / planned * 100, 1) if planned > 0 else 0.0

        subject_progress.append({
            "subject_id": subj["id"],
            "name": subj["name"],
            "color": subj["color"],
            "task_completion_rate": task_rate,
            "time_achievement_rate": time_rate,
            "actual_minutes": actual,
            "planned_minutes": planned,
        })

    return {
        "countdown_days": countdown_days,
        "streak_days": streak,
        "today_minutes": today_minutes,
        "today_tasks_count": today_tasks_count,
        "subject_progress": subject_progress,
        "today_tasks": [dict(t) for t in today_tasks],
    }


@router.get("/heatmap")
def get_heatmap(
    year: int = Query(...),
    month: int = Query(...),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    start_date = date(year, month, 1).isoformat()
    if month == 12:
        end_date = date(year + 1, 1, 1).isoformat()
    else:
        end_date = date(year, month + 1, 1).isoformat()

    rows = db.execute(
        """SELECT date(started_at) as d, COALESCE(SUM(duration_seconds), 0) / 60 as minutes
           FROM pomodoro_sessions
           WHERE type = 'focus' AND date(started_at) >= ? AND date(started_at) < ?
           GROUP BY date(started_at) ORDER BY d""",
        (start_date, end_date)
    ).fetchall()
    return [{"date": r["d"], "minutes": round(r["minutes"], 1)} for r in rows]


@router.get("/weekly-report")
def get_weekly_report(
    date_param: str = Query(..., alias="date"),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    ref_date = datetime.strptime(date_param, "%Y-%m-%d").date()
    week_start = ref_date - timedelta(days=ref_date.weekday())
    week_end = week_start + timedelta(days=6)

    daily_breakdown = []
    d = week_start
    total_minutes = 0
    total_tasks = 0
    while d <= week_end:
        day_str = d.isoformat()
        row = db.execute(
            "SELECT COALESCE(SUM(duration_seconds), 0) as sec FROM pomodoro_sessions "
            "WHERE type = 'focus' AND date(started_at) = ?",
            (day_str,)
        ).fetchone()
        mins = row["sec"] // 60 if row else 0
        tasks_done = db.execute(
            "SELECT COUNT(*) as c FROM tasks WHERE status = 'done' AND date(updated_at) = ?",
            (day_str,)
        ).fetchone()["c"]
        daily_breakdown.append({
            "date": day_str,
            "minutes": mins,
            "tasks_completed": tasks_done,
        })
        total_minutes += mins
        total_tasks += tasks_done
        d += timedelta(days=1)

    subjects = db.execute("SELECT * FROM subjects ORDER BY sort_order").fetchall()
    subject_breakdown = []
    for subj in subjects:
        row = db.execute(
            "SELECT COALESCE(SUM(duration_seconds), 0) as sec FROM pomodoro_sessions "
            "WHERE subject_id = ? AND type = 'focus' AND date(started_at) >= ? AND date(started_at) <= ?",
            (subj["id"], week_start.isoformat(), week_end.isoformat())
        ).fetchone()
        subject_breakdown.append({
            "name": subj["name"],
            "color": subj["color"],
            "minutes": row["sec"] // 60 if row else 0,
        })

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "total_minutes": total_minutes,
        "total_tasks_completed": total_tasks,
        "daily_breakdown": daily_breakdown,
        "subject_breakdown": subject_breakdown,
    }


@router.get("/monthly-report")
def get_monthly_report(
    month: str = Query(...),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    year, mon = map(int, month.split("-"))
    month_start = date(year, mon, 1)
    if mon == 12:
        month_end = date(year + 1, 1, 1)
    else:
        month_end = date(year, mon + 1, 1)

    row = db.execute(
        "SELECT COALESCE(SUM(duration_seconds), 0) as sec FROM pomodoro_sessions "
        "WHERE type = 'focus' AND date(started_at) >= ? AND date(started_at) < ?",
        (month_start.isoformat(), month_end.isoformat())
    ).fetchone()
    total_minutes = row["sec"] // 60 if row else 0

    tasks_done = db.execute(
        "SELECT COUNT(*) as c FROM tasks WHERE status = 'done' "
        "AND date(updated_at) >= ? AND date(updated_at) < ?",
        (month_start.isoformat(), month_end.isoformat())
    ).fetchone()["c"]

    # Daily breakdown
    daily_breakdown = []
    d = month_start
    while d < month_end:
        day_str = d.isoformat()
        r = db.execute(
            "SELECT COALESCE(SUM(duration_seconds), 0) as sec FROM pomodoro_sessions "
            "WHERE type = 'focus' AND date(started_at) = ?", (day_str,)
        ).fetchone()
        mins = r["sec"] // 60 if r else 0
        t = db.execute(
            "SELECT COUNT(*) as c FROM tasks WHERE status = 'done' AND date(updated_at) = ?",
            (day_str,)
        ).fetchone()["c"]
        daily_breakdown.append({"date": day_str, "minutes": mins, "tasks_completed": t})
        d += timedelta(days=1)

    subjects = db.execute("SELECT * FROM subjects ORDER BY sort_order").fetchall()
    subject_breakdown = []
    for subj in subjects:
        r = db.execute(
            "SELECT COALESCE(SUM(duration_seconds), 0) as sec FROM pomodoro_sessions "
            "WHERE subject_id = ? AND type = 'focus' AND date(started_at) >= ? AND date(started_at) < ?",
            (subj["id"], month_start.isoformat(), month_end.isoformat())
        ).fetchone()
        subject_breakdown.append({
            "name": subj["name"], "color": subj["color"],
            "minutes": r["sec"] // 60 if r else 0,
        })

    return {
        "month": month,
        "total_minutes": total_minutes,
        "total_tasks_completed": tasks_done,
        "daily_breakdown": daily_breakdown,
        "subject_breakdown": subject_breakdown,
    }
