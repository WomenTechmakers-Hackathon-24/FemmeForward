export interface QuizData {
    questions: Question[];
  }
  
  export interface Question {
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