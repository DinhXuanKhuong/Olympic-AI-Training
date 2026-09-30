import json
import secrets
import threading
import time
from collections import Counter

from fastapi import HTTPException

from app.database import connection
from app.schemas import FlashcardQuestion, PublicQuestion

_check_tokens: dict[str, tuple[str, float]] = {}
_token_lock = threading.Lock()


def row_to_public(row) -> PublicQuestion:
    data = dict(row)
    data.pop("correct_answer", None)
    data["tags"] = json.loads(data["tags"])
    return PublicQuestion.model_validate(data)


def categories():
    with connection() as db:
        rows = db.execute("SELECT category, subcategory, difficulty FROM questions ORDER BY category").fetchall()
    grouped = {}
    for row in rows:
        entry = grouped.setdefault(row["category"], {"name": row["category"], "question_count": 0, "subcategories": set(), "difficulty_counts": Counter()})
        entry["question_count"] += 1
        entry["subcategories"].add(row["subcategory"])
        entry["difficulty_counts"][row["difficulty"]] += 1
    return [{**entry, "subcategories": sorted(entry["subcategories"]), "difficulty_counts": dict(entry["difficulty_counts"])} for entry in grouped.values()]


def validate_categories(names: list[str]):
    known = {item["name"] for item in categories()}
    invalid = sorted(set(names) - known)
    if invalid:
        raise HTTPException(422, detail=f"Unknown categories: {', '.join(invalid)}")


def random_flashcard(names: list[str], exclude_ids: list[str]):
    validate_categories(names)
    placeholders = ",".join("?" for _ in names)
    sql = f"SELECT * FROM questions WHERE category IN ({placeholders})"
    with connection() as db:
        rows = db.execute(sql, names).fetchall()
    excluded = set(exclude_ids)
    eligible = [row for row in rows if row["id"] not in excluded]
    row = secrets.choice(eligible) if eligible else None
    if row is None:
        raise HTTPException(404, detail="No unseen questions remain in these categories. Restart practice to see them again.")
    token = secrets.token_urlsafe(24)
    now = time.time()
    with _token_lock:
        for old in [key for key, (_, expiry) in _check_tokens.items() if expiry < now]:
            del _check_tokens[old]
        _check_tokens[token] = (row["id"], now + 1800)
    return FlashcardQuestion(**row_to_public(row).model_dump(), check_token=token)


def check_flashcard(question_id: str, answer: str, token: str):
    with _token_lock:
        issued = _check_tokens.pop(token, None)
    if issued is None or issued[0] != question_id or issued[1] < time.time():
        raise HTTPException(404, detail="Practice question expired. Please load another question.")
    row = get_question(question_id)
    return {"correct": answer == row["correct_answer"], "selected_answer": answer, "correct_answer": row["correct_answer"]}


def get_question(question_id: str):
    with connection() as db:
        row = db.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
    if row is None:
        raise HTTPException(404, detail="Question not found")
    return row
