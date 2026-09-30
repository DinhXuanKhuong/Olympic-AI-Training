import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import exams
from scripts.import_questions import import_bank, load_bank


def sample(identifier: str, category: str = "Machine Learning", answer: str = "B"):
    return {"id": identifier, "question": f"Question {identifier}?", "option_a": "A option", "option_b": "B option", "option_c": "C option", "option_d": "D option", "correct_answer": answer, "category": category, "subcategory": "Core", "difficulty": "medium", "tags": [" Sample Tag ", "sample-tag"]}


@pytest.fixture
def bank(tmp_path, monkeypatch):
    db = tmp_path / "questions.db"
    directory = tmp_path / "bank"
    directory.mkdir()
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("QUESTION_BANK_PATH", str(directory))
    exams._sessions.clear()
    return directory


@pytest.fixture
def populated(bank):
    for index, category in enumerate(("Machine Learning", "Deep Learning", "Computer Vision", "NLP", "LLM", "Optimization")):
        data = [sample(f"q{index}_{number:03d}", category) for number in range(25)]
        (bank / f"group{index}.json").write_text(json.dumps(data))
    import_bank(bank)
    with TestClient(app) as client:
        yield client


def test_import_valid_update_and_delete(bank):
    file = bank / "questions.json"
    file.write_text(json.dumps([sample("ml_1"), sample("ml_2")]))
    first = import_bank(bank)
    assert (first["inserted"], first["unchanged"]) == (2, 0)
    assert import_bank(bank)["unchanged"] == 2
    updated = sample("ml_1")
    updated["question"] = "Changed?"
    file.write_text(json.dumps([updated]))
    summary = import_bank(bank)
    assert (summary["updated"], summary["deleted"]) == (1, 1)


def test_duplicate_ids_fail_without_writing(bank):
    (bank / "one.json").write_text(json.dumps([sample("dup")]))
    (bank / "two.json").write_text(json.dumps([sample("dup")]))
    with pytest.raises(ValueError, match="two.json.*dup.*duplicate ID"):
        import_bank(bank)
    assert not (bank.parent / "questions.db").exists()


def test_invalid_answer_and_malformed_json(bank):
    (bank / "bad.json").write_text(json.dumps([sample("bad", answer="E")]))
    with pytest.raises(ValueError, match="bad.json.*bad"):
        load_bank(bank)
    (bank / "bad.json").write_text("{")
    with pytest.raises(ValueError, match="bad.json"):
        load_bank(bank)


def test_category_discovery(populated):
    response = populated.get("/api/categories")
    assert response.status_code == 200
    assert len(response.json()) == 6
    assert all(item["question_count"] == 25 for item in response.json())


def test_flashcard_multiple_categories_and_excludes(populated):
    first = populated.post("/api/flashcards/question", json={"categories": ["NLP", "LLM"], "exclude_ids": []})
    assert first.status_code == 200
    assert first.json()["category"] in ("NLP", "LLM")
    assert "correct_answer" not in first.json()
    second = populated.post("/api/flashcards/question", json={"categories": ["NLP", "LLM"], "exclude_ids": [first.json()["id"]]})
    assert second.json()["id"] != first.json()["id"]
    exhausted = populated.post("/api/flashcards/question", json={"categories": ["NLP"], "exclude_ids": [f"q3_{i:03d}" for i in range(25)]})
    assert exhausted.status_code == 404
    check = populated.post("/api/flashcards/check", json={"question_id": first.json()["id"], "answer": "B", "check_token": first.json()["check_token"]})
    assert check.json()["correct"] is True
    assert populated.post("/api/flashcards/check", json={"question_id": first.json()["id"], "answer": "B", "check_token": first.json()["check_token"]}).status_code == 404
    assert populated.post("/api/flashcards/check", json={"question_id": second.json()["id"], "answer": "E", "check_token": second.json()["check_token"]}).status_code == 422
    assert populated.post("/api/flashcards/check", json={"question_id": second.json()["id"], "answer": "B", "check_token": "made-up"}).status_code == 404


@pytest.mark.parametrize("mode,total", [("60_min", 40), ("180_min", 100)])
def test_exam_generation_and_no_answer_leak(populated, mode, total):
    names = [item["name"] for item in populated.get("/api/categories").json()]
    distribution = {name: 100 // len(names) + (index < 100 % len(names)) for index, name in enumerate(names)}
    response = populated.post("/api/exams/generate", json={"mode": mode, "category_distribution": distribution})
    assert response.status_code == 200
    payload = response.json()
    assert payload["question_count"] == total
    assert len(payload["questions"]) == total
    assert len({question["id"] for question in payload["questions"]}) == total
    assert all("correct_answer" not in question for question in payload["questions"])
    assert sum(payload["category_counts"].values()) == total


def test_largest_remainder_and_invalid_distribution(populated):
    assert exams.allocate(40, {"A": 34, "B": 33, "C": 33}) == {"A": 14, "B": 13, "C": 13}
    assert exams.allocate(100, {"A": 34, "B": 33, "C": 33}) == {"A": 34, "B": 33, "C": 33}
    response = populated.post("/api/exams/generate", json={"mode": "60_min", "category_distribution": {"NLP": 99}})
    assert response.status_code == 422
    assert populated.post("/api/exams/generate", json={"mode": "60_min", "category_distribution": {"NLP": "100"}}).status_code == 422


def test_insufficient_pool_and_unknown_category(populated):
    response = populated.post("/api/exams/generate", json={"mode": "60_min", "category_distribution": {"NLP": 100}})
    assert response.status_code == 422
    assert "requested 40" in response.json()["detail"]
    response = populated.post("/api/exams/generate", json={"mode": "60_min", "category_distribution": {"Unknown": 100}})
    assert response.status_code == 422


def test_scoring_unanswered_and_session(populated):
    generated = populated.post("/api/exams/generate", json={"mode": "60_min", "category_distribution": {"NLP": 50, "LLM": 50}}).json()
    ids = [item["id"] for item in generated["questions"]]
    answers = {ids[0]: "B", ids[1]: "A"}
    response = populated.post(f"/api/exams/{generated['exam_id']}/submit", json={"answers": answers})
    result = response.json()
    assert response.status_code == 200
    assert (result["score"], result["correct"], result["incorrect"], result["unanswered"]) == (1, 1, 1, 38)
    assert result["percentage"] == 2.5
    assert len(result["results"]) == 40
    assert populated.post(f"/api/exams/{generated['exam_id']}/submit", json={"answers": answers}).json() == result
    assert populated.post("/api/exams/missing/submit", json={"answers": {}}).status_code == 404
    exams._sessions[generated["exam_id"]].expires_at = 0
    assert populated.post(f"/api/exams/{generated['exam_id']}/submit", json={"answers": {}}).status_code == 404


def test_website_root_and_client_route(bank, tmp_path, monkeypatch):
    import importlib

    module = importlib.import_module("app.main")
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html><body>Exam Practice</body></html>")
    monkeypatch.setattr(module, "FRONTEND_DIST", dist)
    with TestClient(app) as client:
        assert "Exam Practice" in client.get("/").text
        assert "Exam Practice" in client.get("/exam/60/setup").text
        assert client.get("/api/unknown").status_code == 404
        assert client.get("/docs").status_code == 200
