from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.services.spaced_repetition import get_due_items_query
import sqlite3

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    subject_id: Optional[int] = None
    phase: str = "foundation"
    priority: int = Field(default=0, ge=0, le=2)
    due_date: Optional[str] = None
    estimated_minutes: int = 0
    sort_order: int = 0


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject_id: Optional[int] = None
    phase: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[str] = None
    estimated_minutes: Optional[int] = None
    sort_order: Optional[int] = None


class StatusUpdate(BaseModel):
    status: str = Field(...)


class BatchDelete(BaseModel):
    ids: list[int]

class BatchStatus(BaseModel):
    ids: list[int]
    status: str

class ReorderItem(BaseModel):
    id: int
    sort_order: int


def task_to_dict(row) -> dict:
    d = dict(row)
    return d


@router.get("")
def list_tasks(
    phase: Optional[str] = Query(None),
    subject_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    date_param: Optional[str] = Query(None, alias="date"),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = """SELECT t.*, s.name as subject_name, s.color as subject_color
               FROM tasks t LEFT JOIN subjects s ON t.subject_id = s.id WHERE 1=1"""
    params = []
    if phase:
        query += " AND t.phase = ?"
        params.append(phase)
    if subject_id is not None:
        query += " AND t.subject_id = ?"
        params.append(subject_id)
    if status:
        query += " AND t.status = ?"
        params.append(status)
    if date_param:
        query += " AND t.due_date = ?"
        params.append(date_param)
    query += " ORDER BY CASE WHEN t.status = 'done' THEN 1 ELSE 0 END, t.updated_at DESC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]


@router.post("")
def create_task(
    task: TaskCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.execute(
        """INSERT INTO tasks (title, description, subject_id, phase, priority, due_date,
           estimated_minutes, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (task.title, task.description, task.subject_id, task.phase,
         task.priority, task.due_date, task.estimated_minutes, task.sort_order)
    )
    row = db.execute("""SELECT t.*, s.name as subject_name, s.color as subject_color
                        FROM tasks t LEFT JOIN subjects s ON t.subject_id = s.id
                        WHERE t.id = ?""", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.post("/batch-delete")
def batch_delete_tasks(
    body: BatchDelete,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    placeholders = ",".join("?" * len(body.ids))
    db.execute(f"DELETE FROM tasks WHERE id IN ({placeholders})", body.ids)
    return {"message": f"Deleted {len(body.ids)} tasks"}


@router.post("/batch-status")
def batch_update_status(
    body: BatchStatus,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if body.status not in ("todo", "in_progress", "done"):
        raise HTTPException(status_code=400, detail="Invalid status")
    placeholders = ",".join("?" * len(body.ids))
    now = datetime.now().isoformat()
    db.execute(f"UPDATE tasks SET status = ?, updated_at = ? WHERE id IN ({placeholders})",
               [body.status, now] + body.ids)
    return {"message": f"Updated {len(body.ids)} tasks to {body.status}"}


@router.put("/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    row = db.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    updates = {}
    for field, value in task.model_dump(exclude_unset=True).items():
        updates[field] = value
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        update_values = list(updates.values())
        update_values.append(task_id)
        update_values.append(datetime.now().isoformat())
        db.execute(
            f"UPDATE tasks SET {set_clause}, updated_at = ? WHERE id = ?",
            update_values
        )
    row = db.execute("""SELECT t.*, s.name as subject_name, s.color as subject_color
                        FROM tasks t LEFT JOIN subjects s ON t.subject_id = s.id
                        WHERE t.id = ?""", (task_id,)).fetchone()
    return dict(row)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    row = db.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return {"message": "Task deleted", "id": task_id}


@router.patch("/{task_id}/add-today")
def add_task_to_today(
    task_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from datetime import date
    today = date.today().isoformat()
    row = db.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    db.execute("UPDATE tasks SET added_to_today = ? WHERE id = ?", (today, task_id))
    return {"message": "Added to today", "id": task_id}


@router.patch("/{task_id}/remove-today")
def remove_task_from_today(
    task_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    row = db.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    db.execute("UPDATE tasks SET added_to_today = NULL WHERE id = ?", (task_id,))
    return {"message": "Removed from today", "id": task_id}


@router.patch("/{task_id}/status")
def update_task_status(
    task_id: int,
    body: StatusUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    row = db.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    if body.status not in ("todo", "in_progress", "done"):
        raise HTTPException(status_code=400, detail="Invalid status")
    db.execute(
        "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
        (body.status, datetime.now().isoformat(), task_id)
    )
    row = db.execute("""SELECT t.*, s.name as subject_name, s.color as subject_color
                        FROM tasks t LEFT JOIN subjects s ON t.subject_id = s.id
                        WHERE t.id = ?""", (task_id,)).fetchone()
    return dict(row)


@router.patch("/reorder")
def reorder_tasks(
    items: List[ReorderItem],
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    for item in items:
        db.execute("UPDATE tasks SET sort_order = ? WHERE id = ?", (item.sort_order, item.id))
    return {"message": f"Reordered {len(items)} tasks"}


@router.get("/calendar")
def calendar_tasks(
    start: str = Query(...),
    end: str = Query(...),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    rows = db.execute(
        """SELECT t.*, s.name as subject_name, s.color as subject_color
           FROM tasks t LEFT JOIN subjects s ON t.subject_id = s.id
           WHERE t.due_date >= ? AND t.due_date <= ?
           ORDER BY t.due_date, t.sort_order""",
        (start, end)
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/review-due")
def review_due_tasks(
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    today = date.today().isoformat()
    rows = db.execute(
        """SELECT t.*, s.name as subject_name, s.color as subject_color
           FROM tasks t LEFT JOIN subjects s ON t.subject_id = s.id
           WHERE t.next_review_date IS NOT NULL AND date(t.next_review_date) <= date(?)
           ORDER BY t.next_review_date ASC""",
        (today,)
    ).fetchall()
    return [dict(r) for r in rows]
