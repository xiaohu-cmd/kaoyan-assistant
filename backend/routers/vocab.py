from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.services.spaced_repetition import get_next_review_date, get_current_level_from_next_review
import sqlite3

router = APIRouter(prefix="/api/vocab", tags=["vocab"])


class ReviewRequest(BaseModel):
    feedback: str = Field(...)


class CustomWordRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=100)
    phonetic: str = ""
    part_of_speech: str = ""
    meaning: str = Field(..., min_length=1)
    example_sentence: str = ""
    example_translation: str = ""
    frequency_level: str = "mid"


@router.get("")
def list_vocab(
    freq: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    due: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = "SELECT * FROM vocab_words WHERE 1=1"
    params = []
    if freq:
        query += " AND frequency_level = ?"; params.append(freq)
    if status:
        query += " AND status = ?"; params.append(status)
    if search:
        query += " AND (word LIKE ? OR meaning LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if due == "true":
        query += " AND (next_review_date IS NULL OR date(next_review_date) <= date('now'))"
    query += " ORDER BY CASE frequency_level WHEN 'high' THEN 1 WHEN 'mid' THEN 2 WHEN 'low' THEN 3 END, word ASC"
    query += " LIMIT ? OFFSET ?"; params.extend([limit, offset])
    rows = db.execute(query, params).fetchall()
    total = db.execute("SELECT COUNT(*) as c FROM vocab_words").fetchone()["c"]
    return {"items": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}


@router.post("/{word_id}/review")
def review_vocab(
    word_id: int, body: ReviewRequest,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    word = db.execute("SELECT * FROM vocab_words WHERE id = ?", (word_id,)).fetchone()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    current_level = get_current_level_from_next_review(word["next_review_date"])
    new_date, new_level = get_next_review_date(body.feedback, current_level)
    new_status = "mastered" if new_level >= 4 else ("learning" if new_level > 0 else "new")
    new_count = word["review_count"] + 1
    today = date.today().isoformat()
    db.execute(
        "UPDATE vocab_words SET review_count = ?, last_review_date = ?, next_review_date = ?, status = ? WHERE id = ?",
        (new_count, today, new_date, new_status, word_id)
    )
    row = db.execute("SELECT * FROM vocab_words WHERE id = ?", (word_id,)).fetchone()
    return dict(row)


@router.post("/custom")
def add_custom_word(
    body: CustomWordRequest,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM vocab_words WHERE word = ?", (body.word,)).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Word already exists in vocabulary")
    cursor = db.execute(
        """INSERT INTO vocab_words (word, phonetic, part_of_speech, meaning, example_sentence,
           example_translation, frequency_level, is_custom, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'new')""",
        (body.word, body.phonetic, body.part_of_speech, body.meaning,
         body.example_sentence, body.example_translation, body.frequency_level)
    )
    row = db.execute("SELECT * FROM vocab_words WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)
