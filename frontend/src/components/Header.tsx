import { NavLink, useLocation } from "react-router-dom";

export function Header() {
  const { pathname } = useLocation();
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
          <NavLink
            to="/mock-exams"
            className={pathname.startsWith("/exam/") ? "active" : undefined}
          >
            Mock Exams
          </NavLink>
        </nav>
        <span className="header-caption">Academic preparation</span>
      </div>
    </header>
  );
}
