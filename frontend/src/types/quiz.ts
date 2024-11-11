export interface QuizData {
    quiz_id?: string;
    attempt_id?: string;
    questions: Question[];
    status?: string;
  }
  
  export interface Question {
    question_id: string;
    question: string;
    options: string[];
    correct_answer: string;
    expires_at?: Date;
    explanation?: string;
    learning_point?: string;
  }
  
  export interface QuizProps {
    quizData: QuizData;
  }

  export interface QuizResult {
    status: string;
    score: number;
    correct_answers: number;
    total_questions: number;
    completed_at: Date;
  }