export type Answer = "A" | "B" | "C" | "D";
export type Mode = "60_min" | "180_min";

export interface Category {
  name: string;
  question_count: number;
  subcategories: string[];
  difficulty_counts: Record<string, number>;
}

export interface Question {
  id: string;
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  category: string;
  subcategory: string;
  difficulty: string;
  tags: string[];
}

export interface FlashcardQuestion extends Question {
  check_token: string;
}

export interface Exam {
  exam_id: string;
  mode: Mode;
  question_count: number;
  duration_seconds: number;
  category_counts: Record<string, number>;
  questions: Question[];
}

export interface ExamResultItem {
  question_id: string;
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  selected_answer: Answer | null;
  correct_answer: Answer;
  is_correct: boolean;
  category: string;
  subcategory: string;
}

export interface ExamResult {
  score: number;
  total: number;
  percentage: number;
  correct: number;
  incorrect: number;
  unanswered: number;
  results: ExamResultItem[];
}
