import { Link } from "react-router-dom";
import { useCategories } from "../hooks/useCategories";

const modes = [
  {
    icon: "▧",
    label: "Adaptive",
    title: "Flashcard Practice",
    description: "Practice one question at a time with immediate feedback.",
    details: [
      "Choose multiple subjects",
      "Immediate answer feedback",
      "Study at your own pace",
    ],
    path: "/flashcards/setup",
    button: "Start Flashcards",
  },
  {
    icon: "◷",
    label: "Timed",
    title: "60-Minute Exam",
    description:
      "Standard timed session simulating exam conditions with 40 questions.",
    details: [
      "40 unique questions",
      "Strict 60-minute duration",
      "Score breakdown at completion",
    ],
    path: "/exam/60/setup",
    button: "Start 60-Min Exam",
  },
  {
    icon: "▣",
    label: "Full Mock",
    title: "180-Minute Exam",
    description:
      "Complete a 100-question comprehensive diagnostic examination.",
    details: [
      "100 unique questions",
      "Full-length 180 minutes",
      "Detailed answer review",
    ],
    path: "/exam/180/setup",
    button: "Start 180-Min Exam",
  },
];

export function Dashboard() {
  const { categories, loading, error } = useCategories();
  return (
    <div className="container dashboard-page">
      <div className="dashboard-intro">
        <div>
          <p className="eyebrow">
            ● Academic Preparation <span>•</span> Exam Practice
          </p>
          <h1>Ready to practice?</h1>
          <p>Choose a practice mode and continue your preparation.</p>
        </div>
        <div className="intro-stat">
          {loading
            ? "Loading subjects…"
            : error
              ? "Question bank unavailable"
              : `${categories.reduce((sum, item) => sum + item.question_count, 0)} questions across ${categories.length} subjects`}
        </div>
      </div>
      <h2 className="section-title">Available Practice Modes</h2>
      <div className="mode-grid">
        {modes.map((mode, index) => (
          <section className="mode-card panel" key={mode.title}>
            <div className="mode-top">
              <span className="mode-icon">{mode.icon}</span>
              <span className={index === 2 ? "category-pill" : ""}>
                {mode.label}
              </span>
            </div>
            <h3>{mode.title}</h3>
            <p>{mode.description}</p>
            <ul>
              {mode.details.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <Link
              to={mode.path}
              className={`button ${index === 2 ? "primary" : "soft"}`}
            >
              {mode.button}
            </Link>
          </section>
        ))}
      </div>
      <section className="bank-note panel">
        <span className="mode-icon">▤</span>
        <div>
          <strong>Your question bank</strong>
          <p>
            {error ||
              (categories.length
                ? `Ready in ${categories.map((item) => item.name).join(", ")}.`
                : "Import JSON questions into the backend to begin.")}
          </p>
        </div>
      </section>
    </div>
  );
}
