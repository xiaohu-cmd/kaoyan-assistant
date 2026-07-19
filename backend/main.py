from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.database import init_db
from backend.routers import auth, dashboard, tasks, pomodoro, checkins, notes, materials, flashcards, vocab, reading, writing, schools, settings
from backend.routers.auth import get_current_user
import os, uuid, shutil

app = FastAPI(title="考研助手 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(pomodoro.router)
app.include_router(checkins.router)
app.include_router(notes.router)
app.include_router(materials.router)
app.include_router(flashcards.router)
app.include_router(vocab.router)
app.include_router(reading.router)
app.include_router(writing.router)
app.include_router(schools.router)
app.include_router(settings.router)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

@app.on_event("startup")
def startup():
    import sqlite3
    from backend.database import DATABASE_PATH, DATABASE_DIR
    os.makedirs(DATABASE_DIR, exist_ok=True)

    init_db()

    # Use a direct connection for seeding (avoids generator GC issue with get_db)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO subjects (name, color, icon, sort_order) VALUES (?, ?, ?, ?)",
                [
                    ("政治", "#ef4444", "flag", 1),
                    ("英语二", "#f59e0b", "translate", 2),
                    ("数学三", "#3b82f6", "function", 3),
                    ("432统计学", "#22c55e", "bar-chart", 4),
                ]
            )
            conn.commit()
        # Seed vocabulary if table is empty
        vocab_count = conn.execute("SELECT COUNT(*) FROM vocab_words").fetchone()[0]
        if vocab_count == 0:
            import json
            seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_data", "vocab_5500.json")
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    words = json.load(f)
                for w in words:
                    conn.execute(
                        """INSERT INTO vocab_words (word, phonetic, part_of_speech, meaning,
                           example_sentence, example_translation, frequency_level)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (w["word"], w.get("phonetic", ""), w.get("part_of_speech", ""),
                         w["meaning"], w.get("example_sentence", ""),
                         w.get("example_translation", ""), w.get("frequency_level", "mid"))
                    )
                conn.commit()
                print(f"Seeded {len(words)} vocabulary words.")
            except FileNotFoundError:
                print("Warning: vocab_5500.json not found, skipping vocab seeding.")
    finally:
        conn.close()

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

@app.post("/api/upload/image")
def upload_image(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload an image for use in notes (Markdown editor)."""
    ext = os.path.splitext(image.filename or ".png")[1] or ".png"
    if ext.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"):
        ext = ".png"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOADS_DIR, safe_name)
    with open(dest, "wb") as f:
        shutil.copyfileobj(image.file, f)
    return {"url": f"/uploads/{safe_name}"}

if os.path.exists(FRONTEND_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn, os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
