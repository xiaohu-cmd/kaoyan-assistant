from __future__ import annotations
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, Field
from typing import Optional
from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.services.spaced_repetition import get_next_review_date, get_current_level_from_next_review
import sqlite3

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


class FlashcardCreate(BaseModel):
    subject_id: Optional[int] = None
    front_text: str = Field(..., min_length=1)
    back_text: str = Field(..., min_length=1)
    tags: str = ""
    is_vocab: int = 0


class FlashcardUpdate(BaseModel):
    front_text: Optional[str] = None
    back_text: Optional[str] = None
    subject_id: Optional[int] = None
    tags: Optional[str] = None


class ReviewRequest(BaseModel):
    feedback: str = Field(...)  # "forgot", "blurry", "remembered"

class BatchDelete(BaseModel):
    ids: list[int]



@router.get("")
def list_flashcards(
    subject_id: Optional[int] = Query(None),
    tag: Optional[str] = Query(None),
    due: Optional[str] = Query(None),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = """SELECT f.*, s.name as subject_name, s.color as subject_color
               FROM flashcards f LEFT JOIN subjects s ON f.subject_id = s.id WHERE 1=1"""
    params = []
    if subject_id is not None:
        query += " AND f.subject_id = ?"; params.append(subject_id)
    if tag:
        query += " AND f.tags LIKE ?"; params.append(f"%{tag}%")
    if due == "true":
        query += " AND (f.next_review_date IS NULL OR date(f.next_review_date) <= date('now'))"
    query += " ORDER BY f.created_at DESC"
    return [dict(r) for r in db.execute(query, params).fetchall()]


@router.post("")
def create_flashcard(
    card: FlashcardCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    today = date.today().isoformat()
    cursor = db.execute(
        "INSERT INTO flashcards (subject_id, front_text, back_text, tags, is_vocab, next_review_date) VALUES (?, ?, ?, ?, ?, ?)",
        (card.subject_id, card.front_text, card.back_text, card.tags, card.is_vocab, today)
    )
    row = db.execute("""SELECT f.*, s.name as subject_name, s.color as subject_color
                        FROM flashcards f LEFT JOIN subjects s ON f.subject_id = s.id
                        WHERE f.id = ?""", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.post("/batch-delete")
def batch_delete_flashcards(
    body: BatchDelete,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    placeholders = ",".join("?" * len(body.ids))
    db.execute(f"DELETE FROM flashcards WHERE id IN ({placeholders})", body.ids)
    return {"message": f"Deleted {len(body.ids)} flashcards"}


@router.put("/{card_id}")
def update_flashcard(
    card_id: int, card: FlashcardUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM flashcards WHERE id = ?", (card_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    updates = {k: v for k, v in card.model_dump(exclude_unset=True).items()}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [datetime.now().isoformat(), card_id]
        db.execute(f"UPDATE flashcards SET {set_clause}, updated_at = ? WHERE id = ?", vals)
    row = db.execute("""SELECT f.*, s.name as subject_name, s.color as subject_color
                        FROM flashcards f LEFT JOIN subjects s ON f.subject_id = s.id
                        WHERE f.id = ?""", (card_id,)).fetchone()
    return dict(row)


@router.delete("/{card_id}")
def delete_flashcard(
    card_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM flashcards WHERE id = ?", (card_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    db.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))
    return {"message": "Flashcard deleted", "id": card_id}



@router.post("/{card_id}/review")
def review_flashcard(
    card_id: int, body: ReviewRequest,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    card = db.execute("SELECT * FROM flashcards WHERE id = ?", (card_id,)).fetchone()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    current_level = get_current_level_from_next_review(card["next_review_date"])
    new_date, new_level = get_next_review_date(body.feedback, current_level)
    new_count = card["review_count"] + 1
    today = date.today().isoformat()
    db.execute(
        "UPDATE flashcards SET review_count = ?, last_review_date = ?, next_review_date = ?, updated_at = ? WHERE id = ?",
        (new_count, today, new_date, datetime.now().isoformat(), card_id)
    )
    row = db.execute("""SELECT f.*, s.name as subject_name, s.color as subject_color
                        FROM flashcards f LEFT JOIN subjects s ON f.subject_id = s.id
                        WHERE f.id = ?""", (card_id,)).fetchone()
    return dict(row)
