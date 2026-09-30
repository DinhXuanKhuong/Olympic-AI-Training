import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { QuestionCard } from "../components/QuestionCard";
import type { Answer, FlashcardQuestion } from "../types";

export function FlashcardPractice({ categories }: { categories: string[] }) {
  const [question, setQuestion] = useState<FlashcardQuestion | null>(null);
  const [seen, setSeen] = useState<string[]>([]);
  const [selected, setSelected] = useState<Answer | undefined>();
  const [correct, setCorrect] = useState<Answer | undefined>();
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");
  const [exhausted, setExhausted] = useState(false);
  const requestNumber = useRef(0);

  const load = useCallback(
    async (excludeIds: string[]) => {
      const request = ++requestNumber.current;
      setLoading(true);
      setError("");
      setQuestion(null);
      setSelected(undefined);
      setCorrect(undefined);
      setExhausted(false);
      try {
        const next = await api.flashcard(categories, excludeIds);
        if (request === requestNumber.current) {
          setQuestion(next);
          setSeen([...excludeIds, next.id]);
        }
      } catch (reason) {
        if (request === requestNumber.current) {
          const message = (reason as Error).message;
          setExhausted(message.includes("No unseen questions"));
          setError(message);
        }
      } finally {
        if (request === requestNumber.current) setLoading(false);
      }
    },
    [categories],
  );

  useEffect(() => {
    if (categories.length) void load([]);
    return () => {
      requestNumber.current++;
    };
  }, [categories, load]);

  async function select(answer: Answer) {
    if (!question || checking || correct) return;
    setSelected(answer);
    setChecking(true);
    setError("");
    try {
      const result = await api.check(question.id, answer, question.check_token);
      setCorrect(result.correct_answer);
    } catch (reason) {
      setSelected(undefined);
      setError((reason as Error).message);
    } finally {
      setChecking(false);
    }
  }

  return (
    <div className="container flash-page">
      <div className="control-bar panel">
        <div className="control-heading">
          <Link className="text-button" to="/flashcards/setup">
            ←
          </Link>
          <strong>Flashcard Practice</strong>
          <span className="category-pill">
            {categories.length === 1
              ? categories[0]
              : `${categories.length} categories`}
          </span>
        </div>
        <div className="control-progress">
          <span>Question {seen.length}</span>
          <div className="progress-track">
            <div style={{ width: `${Math.min(100, seen.length * 5)}%` }} />
          </div>
        </div>
        <Link className="text-button" to="/">
          Exit Practice ↗
        </Link>
      </div>
      <div className="flash-content">
        {!categories.length ? (
          <section className="panel empty-panel">
            <h2>Choose categories to begin</h2>
            <Link className="button primary" to="/flashcards/setup">
              Practice setup
            </Link>
          </section>
        ) : loading ? (
          <section className="panel empty-panel">
            Loading your next question…
          </section>
        ) : question ? (
          <>
            <QuestionCard
              question={question}
              number={seen.length}
              selected={selected}
              correct={correct}
              onSelect={select}
            />
            <div className="flash-action panel">
              <span>
                {checking
                  ? "Checking answer…"
                  : correct
                    ? selected === correct
                      ? "Correct answer."
                      : `Incorrect. The correct answer is ${correct}.`
                    : "Select an answer to check it immediately."}
              </span>
              {correct && (
                <button
                  className="button primary"
                  onClick={() => void load(seen)}
                >
                  Next Question →
                </button>
              )}
            </div>
          </>
        ) : (
          <section className="panel empty-panel">
            <h2>
              {exhausted
                ? "You have seen every available question."
                : "Unable to load a question"}
            </h2>
            <p>{error}</p>
            {exhausted ? (
              <button
                className="button primary"
                onClick={() => {
                  setSeen([]);
                  void load([]);
                }}
              >
                Restart Practice
              </button>
            ) : (
              <button
                className="button secondary"
                onClick={() => void load(seen)}
              >
                Try Again
              </button>
            )}
          </section>
        )}
      </div>
    </div>
  );
}
