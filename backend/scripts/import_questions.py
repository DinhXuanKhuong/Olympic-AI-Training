"""Validate and synchronize every question_bank/*.json file into SQLite."""

import json
import sys
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import question_bank_path  # noqa: E402
from app.database import connection  # noqa: E402
from app.schemas import Question  # noqa: E402

COLUMNS = ("id", "question", "option_a", "option_b", "option_c", "option_d", "correct_answer", "category", "subcategory", "difficulty", "tags")


def load_bank(directory: Path):
    files = sorted(directory.glob("*.json"))
    if not files:
        raise ValueError(f"No .json files found in {directory}")
    records = {}
    counts = {}
    errors = []
    for file in files:
        try:
            raw = json.loads(file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{file.name}: {exc}")
            continue
        if not isinstance(raw, list):
            errors.append(f"{file.name}: root must be an array")
            continue
        counts[file.name] = len(raw)
        for index, item in enumerate(raw, 1):
            identifier = item.get("id", f"entry #{index}") if isinstance(item, dict) else f"entry #{index}"
            try:
                question = Question.model_validate(item)
            except ValidationError as exc:
                errors.append(f"{file.name} [{identifier}]: {exc.errors()[0]['msg']} ({exc.errors()[0]['loc']})")
                continue
            if question.id in records:
                errors.append(f"{file.name} [{question.id}]: duplicate ID (also in {records[question.id][0]})")
                continue
            records[question.id] = (file.name, question)
    if errors:
        raise ValueError("Question bank validation failed:\n" + "\n".join(errors))
    return counts, [item[1] for item in records.values()]


def import_bank(directory: Path):
    counts, questions = load_bank(directory)
    inserted = updated = unchanged = deleted = 0
    with connection() as db:
        try:
            existing = {row["id"]: tuple(row[column] for column in COLUMNS) for row in db.execute("SELECT * FROM questions")}
            for question in questions:
                record = question.model_dump()
                record["tags"] = json.dumps(record["tags"], ensure_ascii=False, separators=(",", ":"))
                values = tuple(record[column] for column in COLUMNS)
                old = existing.get(question.id)
                if old == values:
                    unchanged += 1
                    continue
                if old is None:
                    inserted += 1
                else:
                    updated += 1
                placeholders = ",".join("?" for _ in COLUMNS)
                updates = ",".join(f"{column}=excluded.{column}" for column in COLUMNS[1:])
                db.execute(f"INSERT INTO questions ({','.join(COLUMNS)}) VALUES ({placeholders}) ON CONFLICT(id) DO UPDATE SET {updates}", values)
            removed = set(existing) - {question.id for question in questions}
            for identifier in removed:
                db.execute("DELETE FROM questions WHERE id = ?", (identifier,))
            deleted = len(removed)
            db.commit()
        except Exception:
            db.rollback()
            raise
    return {"files": counts, "total": len(questions), "inserted": inserted, "updated": updated, "unchanged": unchanged, "deleted": deleted}


if __name__ == "__main__":
    print("Scanning question bank...\n")
    try:
        summary = import_bank(question_bank_path())
    except (ValueError, OSError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    for name, count in summary["files"].items():
        print(f"{name:<28}{count:>5} questions")
    print("\n" + "-" * 40)
    for key in ("total", "inserted", "updated", "unchanged", "deleted"):
        print(f"{key.title()}: {summary[key]}")
    print("Errors: 0\n" + "-" * 40 + "\nImport completed successfully.")
