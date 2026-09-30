import sqlite3
from contextlib import contextmanager

from app.config import database_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL CHECK (correct_answer IN ('A','B','C','D')),
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy','medium','hard')),
    tags TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_questions_category ON questions(category);
CREATE INDEX IF NOT EXISTS ix_questions_subcategory ON questions(subcategory);
CREATE INDEX IF NOT EXISTS ix_questions_difficulty ON questions(difficulty);
"""


@contextmanager
def connection():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    try:
        db.executescript(SCHEMA)
        yield db
    finally:
        db.close()
