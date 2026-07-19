from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, Field
from typing import Optional
from backend.database import get_db
from backend.routers.auth import get_current_user
import sqlite3

router = APIRouter(prefix="/api/reading", tags=["reading"])


class ReadingCreate(BaseModel):
    year: int = Field(...)
    passage_no: int = 1
    type: str = "reading"
    total_questions: int = 0
    wrong_count: int = 0
    score: float = 0.0
    time_spent_minutes: int = 0
    notes: str = ""


class ReadingUpdate(BaseModel):
    year: Optional[int] = None
    passage_no: Optional[int] = None
    type: Optional[str] = None
    total_questions: Optional[int] = None
    wrong_count: Optional[int] = None
    score: Optional[float] = None
    time_spent_minutes: Optional[int] = None
    notes: Optional[str] = None


class SentenceCreate(BaseModel):
    sentence_text: str = Field(..., min_length=1)
    grammar_analysis: str = ""
    translation: str = ""
    marked_words: str = "[]"


class SentenceUpdate(BaseModel):
    sentence_text: Optional[str] = None
    grammar_analysis: Optional[str] = None
    translation: Optional[str] = None
    marked_words: Optional[str] = None

class BatchDelete(BaseModel):
    ids: list[int]



@router.get("")
def list_readings(
    type_param: Optional[str] = Query(None, alias="type"),
    year: Optional[int] = Query(None),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = "SELECT * FROM reading_records WHERE 1=1"
    params = []
    if type_param:
        query += " AND type = ?"; params.append(type_param)
    if year is not None:
        query += " AND year = ?"; params.append(year)
    query += " ORDER BY year DESC, passage_no ASC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]


@router.post("")
def create_reading(
    body: ReadingCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.execute(
        """INSERT INTO reading_records (year, passage_no, type, total_questions, wrong_count, score, time_spent_minutes, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (body.year, body.passage_no, body.type, body.total_questions, body.wrong_count, body.score, body.time_spent_minutes, body.notes)
    )
    row = db.execute("SELECT * FROM reading_records WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.post("/batch-delete")
def batch_delete_reading(
    body: BatchDelete,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    placeholders = ",".join("?" * len(body.ids))
    db.execute(f"DELETE FROM reading_records WHERE id IN ({placeholders})", body.ids)
    return {"message": f"Deleted {len(body.ids)} reading"}

@router.put("/{record_id}")
def update_reading(
    record_id: int, body: ReadingUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM reading_records WHERE id = ?", (record_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Reading record not found")
    updates = {k: v for k, v in body.model_dump(exclude_unset=True).items()}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [record_id]
        db.execute(f"UPDATE reading_records SET {set_clause} WHERE id = ?", vals)
    row = db.execute("SELECT * FROM reading_records WHERE id = ?", (record_id,)).fetchone()
    return dict(row)


@router.delete("/{record_id}")
def delete_reading(
    record_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM reading_records WHERE id = ?", (record_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Reading record not found")
    db.execute("DELETE FROM reading_records WHERE id = ?", (record_id,))
    return {"message": "Reading record deleted", "id": record_id}


@router.get("/{record_id}/sentences")
def list_sentences(
    record_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    rows = db.execute(
        "SELECT * FROM reading_sentences WHERE reading_record_id = ? ORDER BY created_at", (record_id,)
    ).fetchall()
    return [dict(r) for r in rows]


@router.post("/{record_id}/sentences")
def create_sentence(
    record_id: int, body: SentenceCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    rec = db.execute("SELECT id FROM reading_records WHERE id = ?", (record_id,)).fetchone()
    if not rec:
        raise HTTPException(status_code=404, detail="Reading record not found")
    cursor = db.execute(
        "INSERT INTO reading_sentences (reading_record_id, sentence_text, grammar_analysis, translation, marked_words) VALUES (?, ?, ?, ?, ?)",
        (record_id, body.sentence_text, body.grammar_analysis, body.translation, body.marked_words)
    )
    row = db.execute("SELECT * FROM reading_sentences WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.put("/sentences/{sentence_id}")
def update_sentence(
    sentence_id: int, body: SentenceUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM reading_sentences WHERE id = ?", (sentence_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Sentence not found")
    updates = {k: v for k, v in body.model_dump(exclude_unset=True).items()}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [sentence_id]
        db.execute(f"UPDATE reading_sentences SET {set_clause} WHERE id = ?", vals)
    row = db.execute("SELECT * FROM reading_sentences WHERE id = ?", (sentence_id,)).fetchone()
    return dict(row)


@router.delete("/sentences/{sentence_id}")
def delete_sentence(
    sentence_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM reading_sentences WHERE id = ?", (sentence_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Sentence not found")
    db.execute("DELETE FROM reading_sentences WHERE id = ?", (sentence_id,))
    return {"message": "Sentence deleted", "id": sentence_id}


