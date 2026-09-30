import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { QuestionCard } from "../components/QuestionCard";
import type { Answer, Exam, ExamResult } from "../types";

function clock(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours ? `${hours}:` : ""}${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

export function ActiveExam({
  exam,
  endsAt,
  onResult,
}: {
  exam: Exam | null;
  endsAt: number;
  onResult: (result: ExamResult) => void;
}) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, Answer>>({});
  const [flags, setFlags] = useState<string[]>([]);
  const [remaining, setRemaining] = useState(() =>
    Math.max(0, Math.ceil((endsAt - Date.now()) / 1000)),
  );
  const [confirm, setConfirm] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const submitted = useRef(false);
  const navigate = useNavigate();

  const submit = useCallback(async () => {
    if (!exam || submitted.current) return;
    submitted.current = true;
    setSubmitting(true);
    setConfirm(false);
    setError("");
    try {
      const result = await api.submit(exam.exam_id, answers);
      onResult(result);
      navigate("/results");
    } catch (reason) {
      setError((reason as Error).message);
      submitted.current = false;
      setSubmitting(false);
    }
  }, [answers, exam, navigate, onResult]);

  useEffect(() => {
    if (!exam) return;
    const tick = () => {
      const value = Math.max(0, Math.ceil((endsAt - Date.now()) / 1000));
      setRemaining(value);
      if (value === 0) void submit();
    };
    tick();
    const timer = window.setInterval(tick, 1000);
    return () => window.clearInterval(timer);
  }, [endsAt, exam, submit]);

  if (!exam)
    return (
      <div className="container narrow-page">
        <section className="panel empty-panel">
          <h1>No active exam</h1>
          <p>Start a new timed exam from the setup screen.</p>
          <Link className="button primary" to="/exam/60/setup">
            Choose an exam
          </Link>
        </section>
      </div>
    );
  const question = exam.questions[index];
  const answered = Object.keys(answers).length;
  const minutes = exam.mode === "60_min" ? 60 : 180;
  function toggleFlag() {
    setFlags((current) =>
      current.includes(question.id)
        ? current.filter((id) => id !== question.id)
        : [...current, question.id],
    );
  }
  function nextUnanswered() {
    const next = exam!.questions.findIndex((item) => !answers[item.id]);
    if (next >= 0) setIndex(next);
  }
  return (
    <div className="container exam-page">
      <div className="control-bar panel">
        <div>
          <strong>{minutes}-Minute Mock Exam</strong>
          <small>
            {question.category} · {question.subcategory}
          </small>
        </div>
        <div className="control-progress">
          <div className="progress-label">
            <strong>
              Question {index + 1} of {exam.question_count}
            </strong>
            <span>
              {Math.round((answered / exam.question_count) * 100)}% Completed
            </span>
          </div>
          <div className="progress-track">
            <div
              style={{ width: `${(answered / exam.question_count) * 100}%` }}
            />
          </div>
        </div>
        <div className="exam-controls">
          <span
            className={`timer ${remaining < 300 ? "timer-urgent" : ""}`}
            aria-label="Time remaining"
          >
            ◷ {clock(remaining)}
          </span>
          <button className="text-button" onClick={() => setConfirm(true)}>
            Submit Exam
          </button>
        </div>
      </div>
      <div className="exam-layout">
        <main>
          <QuestionCard
            question={question}
            number={index + 1}
            selected={answers[question.id]}
            onSelect={(answer) =>
              setAnswers((current) => ({ ...current, [question.id]: answer }))
            }
            flagged={flags.includes(question.id)}
            onFlag={toggleFlag}
          />
          <div className="exam-info">
            ⓘ Timed examination mode: answers and scoring remain sealed until
            submission.
          </div>
          <div className="exam-actions">
            <button
              className="button secondary"
              disabled={index === 0}
              onClick={() => setIndex(index - 1)}
            >
              ← Previous Question
            </button>
            <button
              className="text-button"
              onClick={() =>
                setAnswers((current) => {
                  const next = { ...current };
                  delete next[question.id];
                  return next;
                })
              }
            >
              Clear Selection
            </button>
            <button
              className="button dark"
              disabled={index === exam.question_count - 1}
              onClick={() => setIndex(index + 1)}
            >
              Next Question →
            </button>
          </div>
        </main>
        <aside className="navigator panel">
          <div className="navigator-title">
            <h2>Question Navigator</h2>
            <span className="category-pill">
              {answered} / {exam.question_count} Answered
            </span>
          </div>
          <div className="nav-legend">
            <span>
              <i className="legend-answered" /> Answered
            </span>
            <span>
              <i /> Unanswered
            </span>
            <span>♧ Flagged</span>
          </div>
          <div
            className={`question-grid ${exam.question_count > 40 ? "long" : ""}`}
          >
            {exam.questions.map((item, position) => (
              <button
                key={item.id}
                type="button"
                aria-label={`Question ${position + 1}${answers[item.id] ? ", answered" : ""}${flags.includes(item.id) ? ", flagged" : ""}`}
                aria-current={position === index ? "step" : undefined}
                className={`${position === index ? "current" : answers[item.id] ? "answered" : ""} ${flags.includes(item.id) ? "flagged" : ""}`}
                onClick={() => setIndex(position)}
              >
                {position + 1}
                {flags.includes(item.id) && <sup>▣</sup>}
              </button>
            ))}
          </div>
          <div className="navigator-bottom">
            <button className="text-button" onClick={nextUnanswered}>
              Jump to Next Unanswered →
            </button>
            <span>{exam.question_count - answered} Remaining</span>
          </div>
          <button className="button dark full" onClick={() => setConfirm(true)}>
            Submit Examination
          </button>
          <p className="navigator-help">
            Review all questions and flagged items before final processing.
          </p>
        </aside>
      </div>
      {error && <p className="error-banner">{error}</p>}
      {submitting && <p className="status-banner">Submitting your exam…</p>}
      {confirm && (
        <div
          className="modal-backdrop"
          role="presentation"
          onMouseDown={() => setConfirm(false)}
        >
          <div
            className="modal panel"
            role="dialog"
            aria-modal="true"
            aria-labelledby="submit-heading"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <h2 id="submit-heading">Submit examination?</h2>
            <p>
              You answered {answered} of {exam.question_count} questions.
              Unanswered questions will count as skipped.
            </p>
            <div className="modal-actions">
              <button
                className="button secondary"
                onClick={() => setConfirm(false)}
              >
                Continue Exam
              </button>
              <button className="button dark" onClick={() => void submit()}>
                Submit Now
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
