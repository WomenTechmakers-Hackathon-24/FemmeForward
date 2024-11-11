import { QuizProps } from '@/types/quiz';
import { useState } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import api from '@/api/axios';
import axios from 'axios';

const Quiz: React.FC<QuizProps> = ({ quizData }) => {
  const [currentQuestion, setCurrentQuestion] = useState<number>(0);
  const [selectedAnswers, setSelectedAnswers] = useState<(string | null)[]>(Array(quizData.questions.length).fill(null));
  const [showFeedback, setShowFeedback] = useState<boolean[]>(Array(quizData.questions.length).fill(false));
  const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
  const [score, setScore] = useState<number>(0);

  const submitAnswer = async (answer: string) => {
    try {
      const response = await api.post(`/submit-answer`, {
        attempt_id: quizData.attempt_id,
        question_index: currentQuestion,
        answer: answer
      });
      response.data // is_correct, correct_answer, explanation
      return;
    } catch (error) {
      if (axios.isAxiosError(error)) {
          console.error('Error starting quiz:', error);
          //setError('Error connecting to the server.');
          //setIsLoading(false);
          return;
        }
    }
  }

  const handleAnswerSelect = (answer: string) => {
    if (selectedAnswers[currentQuestion] !== null) return; // Prevent changing answer
    submitAnswer(answer);

    const updatedAnswers = [...selectedAnswers];
    updatedAnswers[currentQuestion] = answer;
    setSelectedAnswers(updatedAnswers);

    const feedbackCopy = [...showFeedback];
    feedbackCopy[currentQuestion] = true;
    setShowFeedback(feedbackCopy);

    if (answer.slice(0, 2) === quizData.questions[currentQuestion].correct_answer) {
      setScore(prevScore => prevScore + 1);
    }
  };

  const handleNext = () => {
    if (currentQuestion < quizData.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = () => {
    setIsSubmitted(true);
  };

  return (
    <div className="flex flex-col gap-6 p-4">
      {!isSubmitted ? (
        <>
          <Card className="w-[400px] p-4">
            <h2 className="font-semibold mb-4">
              {quizData.questions[currentQuestion].question}
            </h2>
            <div className="flex flex-col gap-2">
              {quizData.questions[currentQuestion].options.map((option, i) => {
                let buttonClass = '';

                if (selectedAnswers[currentQuestion] !== null) {
                  if (option.slice(0, 2) === quizData.questions[currentQuestion].correct_answer) {
                    buttonClass = 'bg-green-500 text-white';
                  } else if (option === selectedAnswers[currentQuestion]) {
                    buttonClass = 'bg-red-500 text-white';
                  }
                }

                return (
                  <Button
                    className={buttonClass}
                    variant="outline"
                    key={i}
                    onClick={() => handleAnswerSelect(option)}
                    disabled={selectedAnswers[currentQuestion] !== null} // Disable if already answered
                  >
                    {option}
                  </Button>
                );
              })}
            </div>
            {showFeedback[currentQuestion] && (
              <div className="mt-2">
                {selectedAnswers[currentQuestion]?.slice(0, 2) === quizData.questions[currentQuestion].correct_answer ? (
                  <p className="text-green-600 font-medium">Correct!</p>
                ) : (
                  <p className="text-red-600 font-medium">Incorrect. {quizData.questions[currentQuestion].explanation}</p>
                )}
              </div>
            )}
          </Card>
          <div className="flex justify-between mt-4">
            <Button
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
            >
              Previous
            </Button>
            {currentQuestion < quizData.questions.length - 1 ? (
              <Button onClick={handleNext} disabled={selectedAnswers[currentQuestion] === null}>Next</Button>
            ) : (
              <Button onClick={handleSubmit} className="bg-blue-500 text-white" disabled={selectedAnswers[currentQuestion] === null}>
                Submit
              </Button>
            )}
          </div>
        </>
      ) : (
        <div>
          <h2 className="text-2xl font-semibold mb-4">Quiz Results</h2>
          <p className="mb-4">You scored {score} out of {quizData.questions.length}.</p>
        </div>
      )}
    </div>
  );
};

export default Quiz;
