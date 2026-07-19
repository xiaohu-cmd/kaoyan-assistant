from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import get_db
from backend.routers.auth import get_current_user
import sqlite3

router = APIRouter(prefix="/api/notes", tags=["notes"])


class NoteCreate(BaseModel):
    type: str = Field(...)  # "note" or "wrong_question"
    subject_id: Optional[int] = None
    title: str = Field(..., min_length=1)
    content: str = ""
    tags: str = ""


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    subject_id: Optional[int] = None
    tags: Optional[str] = None
    mastered: Optional[int] = None


class BatchDelete(BaseModel):
    ids: list[int]


@router.get("")
def list_notes(
    type_param: Optional[str] = Query(None, alias="type"),
    subject_id: Optional[int] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = """SELECT n.*, s.name as subject_name, s.color as subject_color
               FROM notes_and_errors n LEFT JOIN subjects s ON n.subject_id = s.id WHERE 1=1"""
    params = []
    if type_param:
        query += " AND n.type = ?"; params.append(type_param)
    if subject_id is not None:
        query += " AND n.subject_id = ?"; params.append(subject_id)
    if tag:
        query += " AND n.tags LIKE ?"; params.append(f"%{tag}%")
    if search:
        query += " AND (n.title LIKE ? OR n.content LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY n.created_at DESC"
    return [dict(r) for r in db.execute(query, params).fetchall()]


@router.post("")
def create_note(
    note: NoteCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.execute(
        "INSERT INTO notes_and_errors (type, subject_id, title, content, tags) VALUES (?, ?, ?, ?, ?)",
        (note.type, note.subject_id, note.title, note.content, note.tags)
    )
    row = db.execute("""SELECT n.*, s.name as subject_name, s.color as subject_color
                        FROM notes_and_errors n LEFT JOIN subjects s ON n.subject_id = s.id
                        WHERE n.id = ?""", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.post("/batch-delete")
def batch_delete_notes(
    body: BatchDelete,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    placeholders = ",".join("?" * len(body.ids))
    db.execute(f"DELETE FROM notes_and_errors WHERE id IN ({placeholders})", body.ids)
    return {"message": f"Deleted {len(body.ids)} notes"}


@router.put("/{note_id}")
def update_note(
    note_id: int, note: NoteUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM notes_and_errors WHERE id = ?", (note_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")
    updates = {k: v for k, v in note.model_dump(exclude_unset=True).items()}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [datetime.now().isoformat(), note_id]
        db.execute(f"UPDATE notes_and_errors SET {set_clause}, updated_at = ? WHERE id = ?", vals)
    row = db.execute("""SELECT n.*, s.name as subject_name, s.color as subject_color
                        FROM notes_and_errors n LEFT JOIN subjects s ON n.subject_id = s.id
                        WHERE n.id = ?""", (note_id,)).fetchone()
    return dict(row)


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM notes_and_errors WHERE id = ?", (note_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")
    db.execute("DELETE FROM notes_and_errors WHERE id = ?", (note_id,))
    return {"message": "Note deleted", "id": note_id}


class WrongQuestionUpdate(BaseModel):
    mastered: Optional[bool] = None

class BatchDelete(BaseModel):
    ids: list[int]




@router.patch("/{note_id}/wrong")
def increment_wrong(
    note_id: int,
    body: WrongQuestionUpdate = WrongQuestionUpdate(),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT * FROM notes_and_errors WHERE id = ?", (note_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")
    if existing["type"] != "wrong_question":
        raise HTTPException(status_code=400, detail="Only wrong_question type supports wrong count")
    new_count = existing["wrong_count"] + 1
    mastered_val = existing["mastered"]
    if body.mastered is not None:
        mastered_val = 1 if body.mastered else 0
    db.execute(
        "UPDATE notes_and_errors SET wrong_count = ?, mastered = ?, updated_at = ? WHERE id = ?",
        (new_count, mastered_val, datetime.now().isoformat(), note_id)
    )
    row = db.execute("SELECT * FROM notes_and_errors WHERE id = ?", (note_id,)).fetchone()
    return dict(row)
