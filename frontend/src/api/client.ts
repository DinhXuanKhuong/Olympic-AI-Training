import type {
  Answer,
  Category,
  Exam,
  ExamResult,
  FlashcardQuestion,
  Mode,
} from "../types";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}/api${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true",
        ...init?.headers,
      },
    });
  } catch {
    throw new Error(
      "Cannot reach the backend. Check the API URL and start the server.",
    );
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => item.msg).join("; ")
          : `Request failed (${response.status})`;
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export const api = {
  categories: () => request<Category[]>("/categories"),
  flashcard: (categories: string[], excludeIds: string[]) =>
    request<FlashcardQuestion>("/flashcards/question", {
      method: "POST",
      body: JSON.stringify({ categories, exclude_ids: excludeIds }),
    }),
  check: (questionId: string, answer: Answer, checkToken: string) =>
    request<{
      correct: boolean;
      selected_answer: Answer;
      correct_answer: Answer;
    }>("/flashcards/check", {
      method: "POST",
      body: JSON.stringify({
        question_id: questionId,
        answer,
        check_token: checkToken,
      }),
    }),
  generate: (mode: Mode, distribution: Record<string, number>) =>
    request<Exam>("/exams/generate", {
      method: "POST",
      body: JSON.stringify({ mode, category_distribution: distribution }),
    }),
  submit: (examId: string, answers: Record<string, Answer>) =>
    request<ExamResult>(`/exams/${encodeURIComponent(examId)}/submit`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),
};
