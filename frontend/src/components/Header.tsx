import { NavLink } from "react-router-dom";

export function Header() {
  return (
    <header className="site-header">
      <div className="header-inner">
        <NavLink to="/" className="brand">
          <span className="brand-mark">▤</span>
          <span>Exam Practice</span>
        </NavLink>
        <nav aria-label="Primary navigation">
          <NavLink to="/" end>
            Dashboard
          </NavLink>
          <NavLink to="/flashcards/setup">Practice</NavLink>
          <NavLink to="/exam/60/setup">Mock Exams</NavLink>
        </nav>
        <span className="header-caption">Academic preparation</span>
      </div>
    </header>
  );
}
