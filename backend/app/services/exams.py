import random
import secrets
import threading
import time
from dataclasses import dataclass
from math import floor

from fastapi import HTTPException

from app.database import connection
from app.schemas import PublicQuestion
from app.services.questions import categories, row_to_public

MODES = {"60_min": (40, 3600), "180_min": (100, 10800)}
SESSION_GRACE_SECONDS = 300


@dataclass
class Session:
    questions: list[dict]
    expires_at: float
    result: dict | None = None


_sessions: dict[str, Session] = {}
_lock = threading.Lock()


def allocate(total: int, distribution: dict[str, int]) -> dict[str, int]:
    exact = {name: total * percent / 100 for name, percent in distribution.items()}
    counts = {name: floor(value) for name, value in exact.items()}
    remaining = total - sum(counts.values())
    for name in sorted(exact, key=lambda key: (-(exact[key] - counts[key]), key))[:remaining]:
        counts[name] += 1
    return counts


def generate(mode: str, distribution: dict[str, int]):
    total, duration = MODES[mode]
    allocation = allocate(total, distribution)
    available = {item["name"]: item["question_count"] for item in categories()}
    unknown = sorted(set(distribution) - set(available))
    if unknown:
        raise HTTPException(422, detail=f"Unknown categories: {', '.join(unknown)}")
    for name, requested in allocation.items():
        if requested > available[name]:
            raise HTTPException(422, detail=f"{name}: requested {requested} questions; available {available[name]}.")
    selected = []
    with connection() as db:
        for name, requested in allocation.items():
            selected.extend(dict(row) for row in db.execute("SELECT * FROM questions WHERE category = ? ORDER BY RANDOM() LIMIT ?", (name, requested)))
    random.SystemRandom().shuffle(selected)
    exam_id = secrets.token_urlsafe(24)
    now = time.time()
    with _lock:
        for key in [key for key, value in _sessions.items() if value.expires_at < now]:
            del _sessions[key]
        _sessions[exam_id] = Session(selected, now + duration + SESSION_GRACE_SECONDS)
    return {"exam_id": exam_id, "mode": mode, "question_count": total, "duration_seconds": duration, "category_counts": allocation, "questions": [row_to_public(row) for row in selected]}


def submit(exam_id: str, answers: dict[str, str]):
    with _lock:
        session = _sessions.get(exam_id)
        if session is None or session.expires_at < time.time():
            _sessions.pop(exam_id, None)
            raise HTTPException(404, detail="Exam session expired or not found. Please start a new exam.")
        if session.result is not None:
            return session.result
        ids = {row["id"] for row in session.questions}
        extra = set(answers) - ids
        if extra:
            raise HTTPException(422, detail=f"Answers include questions outside this exam: {', '.join(sorted(extra))}")
        results = []
        for row in session.questions:
            selected = answers.get(row["id"])
            results.append({"question_id": row["id"], "question": row["question"], "option_a": row["option_a"], "option_b": row["option_b"], "option_c": row["option_c"], "option_d": row["option_d"], "selected_answer": selected, "correct_answer": row["correct_answer"], "is_correct": selected == row["correct_answer"], "category": row["category"], "subcategory": row["subcategory"]})
        correct = sum(item["is_correct"] for item in results)
        unanswered = sum(item["selected_answer"] is None for item in results)
        total = len(results)
        session.result = {"score": correct, "total": total, "percentage": round(100 * correct / total, 1), "correct": correct, "incorrect": total - correct - unanswered, "unanswered": unanswered, "results": results}
        return session.result
