import type { Answer, Question } from "../types";

const keys: Answer[] = ["A", "B", "C", "D"];

interface Props {
  question: Question;
  number: number;
  selected?: Answer;
  correct?: Answer;
  onSelect?: (answer: Answer) => void;
  flagged?: boolean;
  onFlag?: () => void;
}

export function QuestionCard({
  question,
  number,
  selected,
  correct,
  onSelect,
  flagged,
  onFlag,
}: Props) {
  return (
    <article className="question-card panel">
      <div className="question-meta">
        <div>
          <strong>QUESTION {number}</strong>
          <span className="meta-dot">•</span>
          <span className="category-pill">{question.subcategory}</span>
          <span className="muted">{question.category}</span>
        </div>
        {onFlag && (
          <button className="text-button" onClick={onFlag} type="button">
            {flagged ? "▣" : "♧"} {flagged ? "Flagged" : "Flag for review"}
          </button>
        )}
      </div>
      <h1 className="question-title">{question.question}</h1>
      <div className="options" role="group" aria-label="Answer options">
        {keys.map((key) => {
          const option = question[
            `option_${key.toLowerCase()}` as keyof Question
          ] as string;
          const state =
            correct === key
              ? "correct"
              : correct && selected === key
                ? "incorrect"
                : selected === key
                  ? "selected"
                  : "";
          return (
            <button
              key={key}
              type="button"
              disabled={!onSelect || !!correct}
              onClick={() => onSelect?.(key)}
              className={`answer-option ${state}`}
              aria-pressed={selected === key}
            >
              <span className="answer-badge">{key}</span>
              <span className="answer-text">{option}</span>
              {correct && correct === key && (
                <span className="answer-note">Correct answer</span>
              )}
              {correct && selected === key && correct !== key && (
                <span className="answer-note">Your answer</span>
              )}
            </button>
          );
        })}
      </div>
    </article>
  );
}
