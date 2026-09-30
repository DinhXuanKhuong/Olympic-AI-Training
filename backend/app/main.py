from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import BACKEND_DIR, frontend_origins
from app.database import connection
from app.schemas import CheckRequest, ExamRequest, FlashcardQuestion, FlashcardRequest, SubmitRequest
from app.services import exams, questions


@asynccontextmanager
async def lifespan(_: FastAPI):
    with connection():
        pass
    yield


app = FastAPI(title="Exam Practice API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=frontend_origins(), allow_methods=["GET", "POST"], allow_headers=["Content-Type", "ngrok-skip-browser-warning"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/categories")
def list_categories():
    return questions.categories()


@app.post("/api/flashcards/question", response_model=FlashcardQuestion)
def flashcard_question(request: FlashcardRequest):
    return questions.random_flashcard(request.categories, request.exclude_ids)


@app.post("/api/flashcards/check")
def check_flashcard(request: CheckRequest):
    return questions.check_flashcard(request.question_id, request.answer, request.check_token)


@app.post("/api/exams/generate")
def generate_exam(request: ExamRequest):
    return exams.generate(request.mode, request.category_distribution)


@app.post("/api/exams/{exam_id}/submit")
def submit_exam(exam_id: str, request: SubmitRequest):
    return exams.submit(exam_id, request.answers)


FRONTEND_DIST = BACKEND_DIR.parent / "frontend" / "dist"
if (FRONTEND_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="frontend-assets")


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str):
    index = FRONTEND_DIST / "index.html"
    if path.startswith(("api/", "assets/")) or Path(path).suffix:
        raise HTTPException(404, detail="Not found")
    if not index.is_file():
        raise HTTPException(503, detail="Frontend build missing. Run npm run build in frontend/.")
    return FileResponse(index)
