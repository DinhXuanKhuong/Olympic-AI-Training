import { useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Header } from "./components/Header";
import { ActiveExam } from "./pages/ActiveExam";
import { Dashboard } from "./pages/Dashboard";
import { ExamSetup } from "./pages/ExamSetup";
import { FlashcardPractice } from "./pages/FlashcardPractice";
import { FlashcardSetup } from "./pages/FlashcardSetup";
import { Results } from "./pages/Results";
import type { Exam, ExamResult, Mode } from "./types";

export default function App() {
  const [practiceCategories, setPracticeCategories] = useState<string[]>([]);
  const [exam, setExam] = useState<Exam | null>(null);
  const [endsAt, setEndsAt] = useState(0);
  const [result, setResult] = useState<ExamResult | null>(null);
  const [resultMode, setResultMode] = useState<Mode | null>(null);
  function startExam(next: Exam) {
    setExam(next);
    setEndsAt(Date.now() + next.duration_seconds * 1000);
    setResult(null);
    setResultMode(next.mode);
  }
  function finishExam(next: ExamResult) {
    setResult(next);
    setExam(null);
  }
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route
          path="/flashcards/setup"
          element={<FlashcardSetup onStart={setPracticeCategories} />}
        />
        <Route
          path="/flashcards/practice"
          element={<FlashcardPractice categories={practiceCategories} />}
        />
        <Route
          path="/exam/60/setup"
          element={<ExamSetup mode="60_min" onStart={startExam} />}
        />
        <Route
          path="/exam/180/setup"
          element={<ExamSetup mode="180_min" onStart={startExam} />}
        />
        <Route
          path="/exam/60"
          element={
            <ActiveExam
              exam={exam?.mode === "60_min" ? exam : null}
              endsAt={endsAt}
              onResult={finishExam}
            />
          }
        />
        <Route
          path="/exam/180"
          element={
            <ActiveExam
              exam={exam?.mode === "180_min" ? exam : null}
              endsAt={endsAt}
              onResult={finishExam}
            />
          }
        />
        <Route
          path="/results"
          element={<Results result={result} mode={resultMode} />}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <footer className="site-footer">
        <div className="container">
          <span>Exam Practice © {new Date().getFullYear()}</span>
          <span>Focused academic preparation</span>
        </div>
      </footer>
    </BrowserRouter>
  );
}
