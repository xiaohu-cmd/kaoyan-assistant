from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel, Field, Field
from typing import Optional
from backend.database import get_db
from backend.routers.auth import get_current_user
import sqlite3, os, shutil, uuid

router = APIRouter(prefix="/api/materials", tags=["materials"])

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")


class MaterialCreate(BaseModel):
    title: str = Field(..., min_length=1)
    subject_id: Optional[int] = None
    type: str = "other"
    source_url: str = ""
    author: str = ""
    notes: str = ""


class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    subject_id: Optional[int] = None
    type: Optional[str] = None
    source_url: Optional[str] = None
    author: Optional[str] = None
    notes: Optional[str] = None


class ProgressUpdate(BaseModel):
    reading_progress: int = Field(..., ge=0, le=100)

class BatchDelete(BaseModel):
    ids: list[int]



@router.get("")
def list_materials(
    type_param: Optional[str] = Query(None, alias="type"),
    subject_id: Optional[int] = Query(None),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = """SELECT m.*, s.name as subject_name, s.color as subject_color
               FROM materials m LEFT JOIN subjects s ON m.subject_id = s.id WHERE 1=1"""
    params = []
    if type_param:
        query += " AND m.type = ?"; params.append(type_param)
    if subject_id is not None:
        query += " AND m.subject_id = ?"; params.append(subject_id)
    query += " ORDER BY m.created_at DESC"
    return [dict(r) for r in db.execute(query, params).fetchall()]


@router.post("")
def create_material(
    material: MaterialCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.execute(
        "INSERT INTO materials (title, subject_id, type, source_url, author, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (material.title, material.subject_id, material.type, material.source_url, material.author, material.notes)
    )
    row = db.execute("""SELECT m.*, s.name as subject_name, s.color as subject_color
                        FROM materials m LEFT JOIN subjects s ON m.subject_id = s.id
                        WHERE m.id = ?""", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.post("/batch-delete")
def batch_delete_materials(
    body: BatchDelete,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    placeholders = ",".join("?" * len(body.ids))
    db.execute(f"DELETE FROM materials WHERE id IN ({placeholders})", body.ids)
    return {"message": f"Deleted {len(body.ids)} materials"}


@router.post("/upload")
def create_and_upload(
    title: str = Form(...),
    type: str = Form("other"),
    subject_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1] or ""
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOADS_DIR, safe_name)
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    url_path = f"/uploads/{safe_name}"
    cursor = db.execute(
        "INSERT INTO materials (title, subject_id, type, file_path) VALUES (?, ?, ?, ?)",
        (title, subject_id, type, url_path)
    )
    row = db.execute("""SELECT m.*, s.name as subject_name, s.color as subject_color
                        FROM materials m LEFT JOIN subjects s ON m.subject_id = s.id
                        WHERE m.id = ?""", (cursor.lastrowid,)).fetchone()
    return dict(row)


@router.post("/{material_id}/upload")
def upload_material_file(
    material_id: int,
    file: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT * FROM materials WHERE id = ?", (material_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Material not found")

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1] or ""
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOADS_DIR, safe_name)

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    url_path = f"/uploads/{safe_name}"
    db.execute(
        "UPDATE materials SET file_path = ?, updated_at = ? WHERE id = ?",
        (url_path, datetime.now().isoformat(), material_id)
    )
    row = db.execute("""SELECT m.*, s.name as subject_name, s.color as subject_color
                        FROM materials m LEFT JOIN subjects s ON m.subject_id = s.id
                        WHERE m.id = ?""", (material_id,)).fetchone()
    return dict(row)


@router.put("/{material_id}")
def update_material(
    material_id: int, material: MaterialUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM materials WHERE id = ?", (material_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Material not found")
    updates = {k: v for k, v in material.model_dump(exclude_unset=True).items()}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [datetime.now().isoformat(), material_id]
        db.execute(f"UPDATE materials SET {set_clause}, updated_at = ? WHERE id = ?", vals)
    row = db.execute("""SELECT m.*, s.name as subject_name, s.color as subject_color
                        FROM materials m LEFT JOIN subjects s ON m.subject_id = s.id
                        WHERE m.id = ?""", (material_id,)).fetchone()
    return dict(row)


@router.delete("/{material_id}")
def delete_material(
    material_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT * FROM materials WHERE id = ?", (material_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Material not found")
    if existing["file_path"]:
        full_path = os.path.join(UPLOADS_DIR, existing["file_path"])
        if os.path.exists(full_path):
            os.remove(full_path)
    db.execute("DELETE FROM materials WHERE id = ?", (material_id,))
    return {"message": "Material deleted", "id": material_id}



@router.patch("/{material_id}/progress")
def update_progress(
    material_id: int, body: ProgressUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.execute("SELECT id FROM materials WHERE id = ?", (material_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Material not found")
    db.execute(
        "UPDATE materials SET reading_progress = ?, updated_at = ? WHERE id = ?",
        (body.reading_progress, datetime.now().isoformat(), material_id)
    )
    row = db.execute("""SELECT m.*, s.name as subject_name, s.color as subject_color
                        FROM materials m LEFT JOIN subjects s ON m.subject_id = s.id
                        WHERE m.id = ?""", (material_id,)).fetchone()
    return dict(row)
