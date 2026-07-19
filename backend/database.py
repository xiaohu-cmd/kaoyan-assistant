import sqlite3
import os
from typing import Generator

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DATABASE_PATH = os.path.join(DATABASE_DIR, "kaoyan.db")

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency: yields a sqlite3.Connection with row factory set."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    """Create all tables if they do not exist. Called at application startup."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            icon TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            subject_id INTEGER REFERENCES subjects(id),
            phase TEXT NOT NULL DEFAULT 'foundation' CHECK(phase IN ('foundation','intensive','sprint')),
            priority INTEGER NOT NULL DEFAULT 0 CHECK(priority IN (0,1,2)),
            status TEXT NOT NULL DEFAULT 'todo' CHECK(status IN ('todo','in_progress','done')),
            due_date TEXT,
            estimated_minutes INTEGER DEFAULT 0,
            actual_minutes INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            next_review_date TEXT,
            added_to_today TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pomodoro_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER REFERENCES tasks(id),
            subject_id INTEGER REFERENCES subjects(id),
            duration_seconds INTEGER NOT NULL DEFAULT 0,
            type TEXT NOT NULL DEFAULT 'focus' CHECK(type IN ('focus','short_break','long_break')),
            started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS daily_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_minutes INTEGER DEFAULT 0,
            review_text TEXT DEFAULT '',
            mood TEXT DEFAULT 'neutral' CHECK(mood IN ('great','good','neutral','tired','bad')),
            tomorrow_plan TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS notes_and_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('note','wrong_question')),
            subject_id INTEGER REFERENCES subjects(id),
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            wrong_count INTEGER DEFAULT 0,
            mastered INTEGER DEFAULT 0 CHECK(mastered IN (0,1)),
            next_review_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER REFERENCES subjects(id),
            title TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'other' CHECK(type IN ('pdf','link','book','other')),
            file_path TEXT DEFAULT '',
            source_url TEXT DEFAULT '',
            author TEXT DEFAULT '',
            reading_progress INTEGER DEFAULT 0 CHECK(reading_progress >= 0 AND reading_progress <= 100),
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER REFERENCES subjects(id),
            front_text TEXT NOT NULL,
            back_text TEXT NOT NULL,
            tags TEXT DEFAULT '',
            is_vocab INTEGER DEFAULT 0 CHECK(is_vocab IN (0,1)),
            review_count INTEGER DEFAULT 0,
            last_review_date TEXT,
            next_review_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS vocab_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL UNIQUE,
            phonetic TEXT DEFAULT '',
            part_of_speech TEXT DEFAULT '',
            meaning TEXT NOT NULL,
            example_sentence TEXT DEFAULT '',
            example_translation TEXT DEFAULT '',
            frequency_level TEXT NOT NULL DEFAULT 'mid' CHECK(frequency_level IN ('high','mid','low')),
            is_custom INTEGER DEFAULT 0 CHECK(is_custom IN (0,1)),
            review_count INTEGER DEFAULT 0,
            last_review_date TEXT,
            next_review_date TEXT,
            status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new','learning','mastered'))
        );

        CREATE TABLE IF NOT EXISTS reading_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            passage_no INTEGER DEFAULT 1,
            type TEXT NOT NULL DEFAULT 'reading' CHECK(type IN ('reading','translation','cloze','new_type')),
            total_questions INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0,
            score REAL DEFAULT 0.0,
            time_spent_minutes INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reading_sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reading_record_id INTEGER REFERENCES reading_records(id) ON DELETE CASCADE,
            sentence_text TEXT NOT NULL,
            grammar_analysis TEXT DEFAULT '',
            translation TEXT DEFAULT '',
            marked_words TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS writing_essays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('small','large')),
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            ai_feedback TEXT DEFAULT '{}',
            grammar_errors TEXT DEFAULT '[]',
            vocabulary_score REAL DEFAULT 0.0,
            sentence_score REAL DEFAULT 0.0,
            overall_score REAL DEFAULT 0.0,
            optimized_version TEXT DEFAULT '',
            is_template INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS school_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_name TEXT NOT NULL,
            year INTEGER NOT NULL,
            major TEXT DEFAULT '',
            exam_subjects TEXT DEFAULT '[]',
            admission_line REAL DEFAULT 0.0,
            enrollment_count INTEGER DEFAULT 0,
            applicant_count INTEGER DEFAULT 0,
            reference_books TEXT DEFAULT '[]',
            notes TEXT DEFAULT '',
            announcement_text TEXT DEFAULT '',
            announcement_date TEXT,
            is_pinned INTEGER DEFAULT 0 CHECK(is_pinned IN (0,1))
        );
    ''')
    # Migration: add next_review_date to tasks table if missing
    try:
        conn.execute("ALTER TABLE tasks ADD COLUMN next_review_date TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()
