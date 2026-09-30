import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCategories } from "../hooks/useCategories";

export function FlashcardSetup({
  onStart,
}: {
  onStart: (names: string[]) => void;
}) {
  const { categories, loading, error } = useCategories();
  const [selected, setSelected] = useState<string[]>([]);
  const navigate = useNavigate();
  useEffect(() => {
    if (categories.length) setSelected(categories.map((item) => item.name));
  }, [categories]);
  function toggle(name: string) {
    setSelected((current) =>
      current.includes(name)
        ? current.filter((item) => item !== name)
        : [...current, name],
    );
  }
  function start() {
    onStart(selected);
    navigate("/flashcards/practice");
  }
  return (
    <div className="container narrow-page">
      <div className="page-heading">
        <p className="eyebrow">Practice setup</p>
        <h1>Flashcard Practice</h1>
        <p>Choose one or more subjects. Questions appear in a random order.</p>
      </div>
      <section className="panel setup-panel">
        <div className="setup-header">
          <div>
            <h2>Select categories</h2>
            <p>At least one category is required.</p>
          </div>
          <div className="inline-actions">
            <button
              className="text-button"
              onClick={() => setSelected(categories.map((item) => item.name))}
            >
              Select All
            </button>
            <button className="text-button" onClick={() => setSelected([])}>
              Clear All
            </button>
          </div>
        </div>
        {loading ? (
          <p>Loading categories…</p>
        ) : error ? (
          <p className="error-banner">{error}</p>
        ) : categories.length === 0 ? (
          <p className="empty-state">
            No questions are available. Import a question bank first.
          </p>
        ) : (
          <div className="category-list">
            {categories.map((item) => (
              <label className="category-row" key={item.name}>
                <input
                  type="checkbox"
                  checked={selected.includes(item.name)}
                  onChange={() => toggle(item.name)}
                />
                <span>
                  <strong>{item.name}</strong>
                  <small>{item.subcategories.join(", ")}</small>
                </span>
                <em>{item.question_count} questions</em>
              </label>
            ))}
          </div>
        )}
        <div className="setup-footer">
          <span>
            {selected.length} of {categories.length} categories selected
          </span>
          <button
            className="button primary"
            disabled={!selected.length}
            onClick={start}
          >
            Start Practice →
          </button>
        </div>
      </section>
    </div>
  );
}
