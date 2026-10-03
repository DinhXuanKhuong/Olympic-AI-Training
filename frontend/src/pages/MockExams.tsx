import { Link } from "react-router-dom";

const exams = [
  {
    icon: "◷",
    label: "Timed",
    title: "60-Minute Exam",
    description: "A focused timed session with 40 questions.",
    details: ["60 minutes", "40 unique questions", "Detailed answer review"],
    path: "/exam/60/setup",
    action: "Choose 60-Minute Exam",
  },
  {
    icon: "▣",
    label: "Full Mock",
    title: "180-Minute Exam",
    description: "A full-length timed session with 100 questions.",
    details: ["180 minutes", "100 unique questions", "Detailed answer review"],
    path: "/exam/180/setup",
    action: "Choose 180-Minute Exam",
  },
];

export function MockExams() {
  return (
    <div className="container dashboard-page">
      <div className="page-heading">
        <p className="eyebrow">Academic Preparation</p>
        <h1>Mock Exams</h1>
        <p>Choose an exam length, then set your category distribution.</p>
      </div>
      <div className="mode-grid mock-mode-grid">
        {exams.map((exam) => (
          <section className="mode-card panel" key={exam.path}>
            <div className="mode-top">
              <span className="mode-icon">{exam.icon}</span>
              <span className="category-pill">{exam.label}</span>
            </div>
            <h3>{exam.title}</h3>
            <p>{exam.description}</p>
            <ul>
              {exam.details.map((detail) => (
                <li key={detail}>{detail}</li>
              ))}
            </ul>
            <Link className="button primary" to={exam.path}>
              {exam.action}
            </Link>
          </section>
        ))}
      </div>
    </div>
  );
}
