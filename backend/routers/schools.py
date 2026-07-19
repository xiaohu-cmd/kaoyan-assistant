from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import get_db
from backend.routers.auth import get_current_user
import sqlite3

router = APIRouter(prefix="/api/schools", tags=["schools"])


class SchoolCreate(BaseModel):
    school_name: str = Field(..., min_length=1)
    year: int = Field(...)
    major: str = ""
    exam_subjects: str = "[]"
    admission_line: float = 0.0
    enrollment_count: int = 0
    applicant_count: int = 0
    reference_books: str = "[]"
    notes: str = ""
    announcement_text: str = ""
    announcement_date: Optional[str] = None
    is_pinned: int = 0


class SchoolUpdate(BaseModel):
    school_name: Optional[str] = None
    year: Optional[int] = None
    major: Optional[str] = None
    exam_subjects: Optional[str] = None
    admission_line: Optional[float] = None
    enrollment_count: Optional[int] = None
    applicant_count: Optional[int] = None
    reference_books: Optional[str] = None
    notes: Optional[str] = None
    announcement_text: Optional[str] = None
    announcement_date: Optional[str] = None
    is_pinned: Optional[int] = None


@router.get("")
def list_schools(
    school: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = "SELECT * FROM school_info WHERE 1=1"
    params = []
    if school:
        query += " AND school_name LIKE ?"; params.append(f"%{school}%")
    if year is not None:
        query += " AND year = ?"; params.append(year)
    query += " ORDER BY is_pinned DESC, year DESC"
    return [dict(r) for r in db.execute(query, params).fetchall()]


@router.post("")
def create_school(
    body: SchoolCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.execute(
        """INSERT INTO school_info (school_name, year, major, exam_subjects, admission_line,
           enrollment_count, applicant_count, reference_books, notes, announcement_text,
           announcement_date, is_pinned)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (body.school_name, body.year, body.major, body.exam_subjects, body.admission_line,
         body.enrollment_count, body.applicant_count, body.reference_books, body.notes,
         body.announcement_text, body.announcement_date, body.is_pinned)
    )
    row = db.execute("SELECT * FROM school_info WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.put("/{school_id}")
def update_school(
    school_id: int, body: SchoolUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM school_info WHERE id = ?", (school_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="School not found")
    updates = {k: v for k, v in body.model_dump(exclude_unset=True).items()}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [school_id]
        db.execute(f"UPDATE school_info SET {set_clause} WHERE id = ?", vals)
    row = db.execute("SELECT * FROM school_info WHERE id = ?", (school_id,)).fetchone()
    return dict(row)


@router.delete("/{school_id}")
def delete_school(
    school_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM school_info WHERE id = ?", (school_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="School not found")
    db.execute("DELETE FROM school_info WHERE id = ?", (school_id,))
    return {"message": "School deleted", "id": school_id}
