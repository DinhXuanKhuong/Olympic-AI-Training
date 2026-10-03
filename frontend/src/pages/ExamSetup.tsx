import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useCategories } from "../hooks/useCategories";
import type { Exam, Mode } from "../types";
import { allocation, defaultDistribution } from "../utils/allocation";

export function ExamSetup({
  mode,
  onStart,
}: {
  mode: Mode;
  onStart: (exam: Exam) => void;
}) {
  const { categories, loading, error } = useCategories();
  const [distribution, setDistribution] = useState<Record<string, number>>({});
  const [starting, setStarting] = useState(false);
  const [apiError, setApiError] = useState("");
  const navigate = useNavigate();
  const count = mode === "60_min" ? 40 : 100;
  const minutes = mode === "60_min" ? 60 : 180;
  useEffect(() => {
    if (categories.length)
      setDistribution(defaultDistribution(categories.map((item) => item.name)));
  }, [categories]);
  const assigned = allocation(count, distribution);
  const sum = Object.values(distribution).reduce(
    (total, value) => total + value,
    0,
  );
  const shortage = categories.find(
    (item) => (assigned[item.name] || 0) > item.question_count,
  );
  const valid =
    categories.length > 0 &&
    sum === 100 &&
    !shortage &&
    Object.keys(distribution).length === categories.length &&
    Object.values(distribution).every(
      (value) => Number.isInteger(value) && value >= 0 && value <= 100,
    );

  async function start() {
    setStarting(true);
    setApiError("");
    try {
      const exam = await api.generate(mode, distribution);
      onStart(exam);
      navigate(`/exam/${minutes}`);
    } catch (reason) {
      setApiError((reason as Error).message);
    } finally {
      setStarting(false);
    }
  }
  return (
    <div className="container narrow-page">
      <div className="page-heading">
        <p className="eyebrow">Mock exam setup</p>
        <h1>{minutes}-Minute Mock Exam</h1>
        <p>
          Allocate exactly 100% across the available categories for {count}{" "}
          questions.
        </p>
      </div>
      <section className="panel setup-panel">
        <div className="setup-header">
          <div>
            <h2>Category distribution</h2>
            <p>Question counts use largest remainder rounding.</p>
          </div>
          <span className="category-pill">
            {minutes} minutes · {count} questions
          </span>
        </div>
        {loading ? (
          <p>Loading categories…</p>
        ) : error ? (
          <p className="error-banner">{error}</p>
        ) : categories.length === 0 ? (
          <p className="empty-state">
            No categories are available. Import a question bank first.
          </p>
        ) : (
          <div className="distribution-list">
            {categories.map((item) => (
              <div className="distribution-row" key={item.name}>
                <div>
                  <strong>{item.name}</strong>
                  <small>{item.question_count} available</small>
                </div>
                <div className="ratio-input">
                  <button
                    aria-label={`Decrease ${item.name}`}
                    onClick={() =>
                      setDistribution((current) => ({
                        ...current,
                        [item.name]: Math.max(0, (current[item.name] || 0) - 1),
                      }))
                    }
                  >
                    −
                  </button>
                  <input
                    aria-label={`${item.name} percentage`}
                    type="number"
                    min="0"
                    max="100"
                    value={distribution[item.name] ?? 0}
                    onChange={(event) =>
                      setDistribution((current) => ({
                        ...current,
                        [item.name]: Number(event.target.value),
                      }))
                    }
                  />
                  <span>%</span>
                  <button
                    aria-label={`Increase ${item.name}`}
                    onClick={() =>
                      setDistribution((current) => ({
                        ...current,
                        [item.name]: Math.min(
                          100,
                          (current[item.name] || 0) + 1,
                        ),
                      }))
                    }
                  >
                    +
                  </button>
                </div>
                <div
                  className={`question-count ${assigned[item.name] > item.question_count ? "danger" : ""}`}
                >
                  {assigned[item.name] || 0} questions
                </div>
              </div>
            ))}
          </div>
        )}
        <div className="allocation-total">
          <strong>Total allocation</strong>
          <strong className={sum === 100 ? "success" : "danger"}>
            {sum}% ·{" "}
            {Object.values(assigned).reduce((total, value) => total + value, 0)}{" "}
            questions
          </strong>
        </div>
        {shortage && (
          <p className="error-banner">
            {shortage.name} needs {assigned[shortage.name]} questions; only{" "}
            {shortage.question_count} are available.
          </p>
        )}
        {apiError && <p className="error-banner">{apiError}</p>}
        <div className="setup-footer">
          <span>
            {sum === 100 ? "Distribution ready" : "Percentages must total 100%"}
          </span>
          <button
            className="button primary"
            disabled={!valid || starting}
            onClick={() => void start()}
          >
            {starting ? "Creating exam…" : "Start Exam →"}
          </button>
        </div>
      </section>
    </div>
  );
}
