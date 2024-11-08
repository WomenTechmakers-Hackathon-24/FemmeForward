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
            <div style={{ paddingTop: '750px' }}>
            <h2 className="text-2xl font-semibold mb-4">Quiz Results</h2>
            <p className="mb-4">You scored {score} out of {quizData.questions.length}.</p>
            {quizData.questions.map((question, index) => {
                const isCorrect = selectedAnswers[index]?.slice(0,2) === question.correct_answer;
                return (
                    <div key={index} className="mb-6">
                    <h3 className="font-medium">{question.question}</h3>
                    <ul>
                        {question.options.map((option, i) => {
                        const isSelected = option === selectedAnswers[index];
                        const isWrongSelection = isSelected && !isCorrect;

                        return (
                            <li
                            key={i}
                            className={`p-2 ${option.slice(0,2) === question.correct_answer ? 'font-bold text-green-600' : isWrongSelection ? 'italic text-red-600' : ''}`}
                            >
                            {option}
                            </li>
                        );
                        })}
                    </ul>
                    {!isCorrect && (
                        <p className="mt-2 italic text-gray-700">{question.explanation}</p>
                    )}
                    </div>
                );
})}
          </div>
          )}
        </div>
      );
  };

  export default Quiz;