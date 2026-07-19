from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, Field
from typing import Optional
from backend.database import get_db, DATABASE_PATH
from backend.routers.auth import get_current_user
from backend.services.ai_writing import get_ai_feedback
import sqlite3

router = APIRouter(prefix="/api/writing", tags=["writing"])


class EssayCreate(BaseModel):
    type: str = Field(...)
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class EssayUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None

class BatchDelete(BaseModel):
    ids: list[int]



@router.get("")
def list_essays(
    type_param: Optional[str] = Query(None, alias="type"),
    include_templates: bool = Query(False),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = "SELECT * FROM writing_essays WHERE 1=1"
    params = []
    if not include_templates:
        query += " AND (is_template = 0 OR is_template IS NULL)"
    if type_param:
        query += " AND type = ?"; params.append(type_param)
    query += " ORDER BY created_at DESC"
    return [dict(r) for r in db.execute(query, params).fetchall()]


@router.post("")
def create_essay(
    essay: EssayCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.execute(
        "INSERT INTO writing_essays (type, title, content) VALUES (?, ?, ?)",
        (essay.type, essay.title, essay.content)
    )
    row = db.execute("SELECT * FROM writing_essays WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.post("/batch-delete")
def batch_delete_writing(
    body: BatchDelete,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    placeholders = ",".join("?" * len(body.ids))
    db.execute(f"DELETE FROM writing_essays WHERE id IN ({placeholders})", body.ids)
    return {"message": f"Deleted {len(body.ids)} writing"}


@router.put("/{essay_id}")
def update_essay(
    essay_id: int, essay: EssayUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM writing_essays WHERE id = ?", (essay_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Essay not found")
    updates = {k: v for k, v in essay.model_dump(exclude_unset=True).items()}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [essay_id]
        db.execute(f"UPDATE writing_essays SET {set_clause} WHERE id = ?", vals)
    row = db.execute("SELECT * FROM writing_essays WHERE id = ?", (essay_id,)).fetchone()
    return dict(row)


@router.delete("/{essay_id}")
def delete_essay(
    essay_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM writing_essays WHERE id = ?", (essay_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Essay not found")
    db.execute("DELETE FROM writing_essays WHERE id = ?", (essay_id,))
    return {"message": "Essay deleted", "id": essay_id}



@router.post("/{essay_id}/ai-feedback")
async def request_ai_feedback(
    essay_id: int,
    current_user: dict = Depends(get_current_user)
):
    # Use a direct connection to avoid thread-bound sqlite3 issues in async endpoints
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        essay = conn.execute("SELECT * FROM writing_essays WHERE id = ?", (essay_id,)).fetchone()
        if not essay:
            raise HTTPException(status_code=404, detail="Essay not found")
        essay_content = essay["content"]
        essay_type = essay["type"]
    finally:
        conn.close()

    result = await get_ai_feedback(essay_content, essay_type)

    conn2 = sqlite3.connect(DATABASE_PATH)
    conn2.row_factory = sqlite3.Row
    try:
        conn2.execute(
            """UPDATE writing_essays
               SET ai_feedback = ?, grammar_errors = ?, vocabulary_score = ?, sentence_score = ?,
                   overall_score = ?, optimized_version = ?
               WHERE id = ?""",
            (result["ai_feedback"], result["grammar_errors"], result["vocabulary_score"],
             result["sentence_score"], result["overall_score"], result["optimized_version"], essay_id)
        )
        conn2.commit()
        row = conn2.execute("SELECT * FROM writing_essays WHERE id = ?", (essay_id,)).fetchone()
        return dict(row)
    finally:
        conn2.close()
