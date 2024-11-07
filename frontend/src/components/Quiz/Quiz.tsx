import { QuizProps } from '@/types/quiz';
import { useState } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const Quiz: React.FC<QuizProps> = ({ quizData }) => {
    const [currentQuestion, setCurrentQuestion] = useState<number>(0);
    const [selectedAnswers, setSelectedAnswers] = useState<(string | null)[]>(Array(quizData.questions.length).fill(null));
    const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
    const [score, setScore] = useState<number>(0);
  
    const handleAnswerSelect = (answer: string) => {
      const updatedAnswers = [...selectedAnswers];
      updatedAnswers[currentQuestion] = answer;
      setSelectedAnswers(updatedAnswers);
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
        const unansweredQuestions = selectedAnswers.filter(answer => answer === null);
        if (unansweredQuestions.length > 0) {
          alert('There are unanswered questions. Please review your answers before submitting.');
          return;
        }
        // Calculate the score
        let userScore = 0;
        selectedAnswers.forEach((answer, index) => {
          if (answer?.slice(0,2) === quizData.questions[index].correct_answer) {
            userScore++;
          }
        });
    
        setScore(userScore);
        setIsSubmitted(true);
        console.log('Submitted answers:', selectedAnswers);
      };
  
    return (
        <div className="flex flex-col gap-6 p-4">
          {!isSubmitted ? (
            <>
              <Card className="p-4">
                <h2 className="font-semibold mb-4">
                  {quizData.questions[currentQuestion].question}
                </h2>
                <div className="flex flex-col gap-2">
                  {quizData.questions[currentQuestion].options.map((option, i) => (
                    <Button
                      className={`${
                        selectedAnswers[currentQuestion] === option
                          ? 'bg-blue-500 text-white'
                          : ''
                      }`}
                      variant="outline"
                      key={i}
                      onClick={() => handleAnswerSelect(option)}
                    >
                      {option}
                    </Button>
                  ))}
                </div>
              </Card>
              <div className="flex justify-between mt-4">
                <Button
                  onClick={handlePrevious}
                  disabled={currentQuestion === 0}
                >
                  Previous
                </Button>
                {currentQuestion < quizData.questions.length - 1 ? (
                  <Button onClick={handleNext}>Next</Button>
                ) : (
                  <Button onClick={handleSubmit} className="bg-blue-500 text-white">
                    Submit
                  </Button>
                )}
              </div>
            </>
          ) : (
                <div>
                <h2 className="text-2xl font-semibold mb-4">Quiz Results</h2>
                <p className="mb-4">You scored {score} out of {quizData.questions.length}.</p>
                {quizData.questions.map((question, index) => (
                <div key={index} className="mb-4">
                    <p className="font-medium">{question.question}</p>
                    <p>
                    Your answer: <strong>{selectedAnswers[index] || 'No answer'}</strong>
                    </p>
                    <p>
                    Correct answer: <strong>{question.correct_answer}</strong>
                    </p>
                </div>
                ))}
            </div>
          )}
        </div>
      );
  };

  export default Quiz;