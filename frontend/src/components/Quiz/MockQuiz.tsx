import { QuizData } from "@/types/quiz";

// Mock quiz data
export const mockQuizData: QuizData = {
    questions: [
      {
        question: 'What is the capital of France?',
        options: ['A) Paris', 'B) Berlin', 'C) Madrid', 'D) Rome'],
        correct_answer: 'A)',
        explanation: 'Paris is the capital city of France, known for its culture and landmarks such as the Eiffel Tower.'
      },
      {
        question: 'Which planet is known as the Red Planet?',
        options: ['A) Mars', 'B) Earth', 'C) Venus', 'D) Jupiter'],
        correct_answer: 'A)',
        explanation: 'Mars is called the Red Planet because of its reddish appearance, which comes from iron oxide on its surface.'
      },
      {
        question: 'Who wrote "Hamlet"?',
        options: ['A) Charles Dickens', 'B) Mark Twain', 'C) Jane Austen', 'D) William Shakespeare'],
        correct_answer: 'D)',
        explanation: 'William Shakespeare, an English playwright, wrote "Hamlet," one of his most famous tragedies.'
      },
      {
        question: 'What is the largest ocean on Earth?',
        options: ['A) Atlantic Ocean', 'B) Indian Ocean', 'C) Pacific Ocean', 'D) Arctic Ocean'],
        correct_answer: 'C)',
        explanation: 'The Pacific Ocean is the largest and deepest ocean on Earth, covering more than 60 million square miles.'
      },
      {
        question: 'What is the chemical symbol for gold?',
        options: ['A) Ag','B) Au', 'C) Fe', 'D) Pb'],
        correct_answer: 'B)',
        explanation: 'The chemical symbol for gold is "Au," which comes from the Latin word "Aurum."'
      },
    ],
  };