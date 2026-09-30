import { useState } from "react";
import { Link } from "react-router-dom";
import type { Answer, ExamResult, ExamResultItem, Mode } from "../types";

type Filter = "all" | "incorrect" | "correct" | "unanswered";
const keys: Answer[] = ["A", "B", "C", "D"];

function ReviewCard({
  item,
  number,
}: {
  item: ExamResultItem;
  number: number;
}) {
  const status = !item.selected_answer
    ? "Unanswered"
    : item.is_correct
      ? "Correct"
      : "Incorrect";
  return (
    <article className="review-card panel">
      <div className="review-meta">
        <span className={`result-pill ${status.toLowerCase()}`}>
          Question {number} · {status}
        </span>
        <span>
          {item.category} · {item.subcategory}
        </span>
      </div>
      <h3>{item.question}</h3>
      <div className="review-options">
        {keys.map((key) => (
          <div
            key={key}
            className={`review-option ${item.correct_answer === key ? "correct" : item.selected_answer === key ? "incorrect" : ""}`}
          >
            <span className="answer-badge">{key}</span>
            <span>
              {item[`option_${key.toLowerCase()}` as keyof ExamResultItem]}
            </span>
            <small>
              {item.correct_answer === key
                ? "✓ Correct answer"
                : item.selected_answer === key
                  ? "× Your answer"
                  : ""}
            </small>
          </div>
        ))}
      </div>
      {!item.selected_answer && (
        <p className="muted">No answer was selected.</p>
      )}
    </article>
  );
}

export function Results({
  result,
  mode,
}: {
  result: ExamResult | null;
  mode: Mode | null;
}) {
  const [filter, setFilter] = useState<Filter>("all");
  if (!result)
    return (
      <div className="container narrow-page">
        <section className="panel empty-panel">
          <h1>No results to show</h1>
          <p>Complete a timed exam to see your answer review.</p>
          <Link className="button primary" to="/">
            Back to Dashboard
          </Link>
        </section>
      </div>
    );
  const shown = result.results
    .map((item, index) => ({ item, number: index + 1 }))
    .filter(
      ({ item }) =>
        filter === "all" ||
        (filter === "unanswered"
          ? !item.selected_answer
          : filter === "correct"
            ? item.is_correct
            : !!item.selected_answer && !item.is_correct),
    );
  const modeLabel = mode === "180_min" ? "180-Minute" : "60-Minute";
  return (
    <div className="container results-page">
      <div className="result-heading">
        <span className="mode-icon">▤</span>
        <strong>{modeLabel} Mock Exam</strong>
        <span>• Completed</span>
      </div>
      <section className="result-summary panel">
        <div className="score-block">
          <div className="score-top">
            <span className="eyebrow">Final Result</span>
            <span className="result-pill correct">
              {result.percentage}% Accuracy
            </span>
          </div>
          <div className="score-line">
            <strong>{result.score}</strong>
            <span>/ {result.total}</span>
          </div>
          <h2>
            {result.percentage >= 80
              ? "Excellent readiness"
              : "Keep practicing"}
          </h2>
          <p>Your score is based on the answers submitted for this exam.</p>
          <div className="score-track">
            <div style={{ width: `${result.percentage}%` }} />
          </div>
          <div className="summary-actions">
            <a className="button primary" href="#answer-review">
              Review All {result.total} Answers
            </a>
            <Link
              className="button secondary"
              to={mode === "180_min" ? "/exam/180/setup" : "/exam/60/setup"}
            >
              Retake Exam
            </Link>
            <Link className="text-button" to="/">
              ← Back to Dashboard
            </Link>
          </div>
        </div>
        <div className="stat-grid">
          <div>
            <span>Correct Answers</span>
            <strong>{result.correct}</strong>
            <small>items</small>
          </div>
          <div>
            <span>Incorrect Answers</span>
            <strong>{result.incorrect}</strong>
            <small>items</small>
          </div>
          <div>
            <span>Unanswered</span>
            <strong>{result.unanswered}</strong>
            <small>skipped</small>
          </div>
          <div>
            <span>Accuracy</span>
            <strong>{result.percentage}%</strong>
            <small>of all questions</small>
          </div>
        </div>
      </section>
      <section className="answer-review" id="answer-review">
        <div className="review-heading">
          <div>
            <h2>Detailed Answer Breakdown</h2>
            <p>
              Filter by response validity to review every question and answer.
            </p>
          </div>
          <div className="filter-tabs">
            {(
              [
                ["all", "All Questions", result.total],
                ["incorrect", "Incorrect", result.incorrect],
                ["correct", "Correct", result.correct],
                ["unanswered", "Unanswered", result.unanswered],
              ] as [Filter, string, number][]
            ).map(([key, label, count]) => (
              <button
                className={filter === key ? "active" : ""}
                key={key}
                onClick={() => setFilter(key)}
              >
                {label} ({count})
              </button>
            ))}
          </div>
        </div>
        {shown.length ? (
          shown.map(({ item, number }) => (
            <ReviewCard key={item.question_id} item={item} number={number} />
          ))
        ) : (
          <div className="panel empty-panel">
            No questions match this filter.
          </div>
        )}
      </section>
    </div>
  );
}
