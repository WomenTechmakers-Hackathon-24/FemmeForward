import api from '@/api/axios';
import { QuizData } from '@/types/quiz';
import axios from 'axios';
import { useEffect, useState } from 'react';
import Quiz from './Quiz';
import LoadingSpinner from '../ui/LoadingSpinner';

interface QuizComponentProps {
  topic: string; // The title of the topic selected for the quiz
}

const QuizComponent: React.FC<QuizComponentProps> = ({topic}) => {
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasStarted, setHasStarted] = useState<boolean>(false);

  const GenerateQuiz = async (): Promise<string | null> => {
    setIsLoading(true);
    try {
      const response = await api.post(`/generate_quiz`, {
        topic: topic,
        num_questions: 5
      });
      const quizId = response.data;
      if (quizId) {
        setQuizData((prev) => ({ ...prev, quiz_id: quizId, questions: prev?.questions || [] }));
        setError(null);
        return quizId; // Indicate success
      } else {
        setError('Invalid quiz ID received.');
        setQuizData(null);
        return null; // Indicate failure
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('Error generating quiz:', error);
        setError('Error connecting to the server.');
      }
      setQuizData(null);
      return null; // Indicate failure
    } finally {
      setIsLoading(false);
    }
  };

  const GetQuiz = async (quizId: string) => {
    if (!quizId) {
      setError("Quiz not generated properly");
      return;
    }
    setIsLoading(true);
    try {
      const response = await api.get(`/quiz/` + quizId);
      setQuizData((prev) => ({ ...prev, questions: response.data }));
      setError(null);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('Error getting quiz data:', error);
        setError('Error connecting to the server.');
        setQuizData(null);
      }
    } finally {
      setIsLoading(false);
    }
  };

    const startQuiz = async () => {
      try {
        const response = await api.post(`/quiz/start`, {
          quiz_id: quizData?.quiz_id
        });
        setQuizData((prev) => ({...prev, attempt_id: response.data.attempt_id, status: response.data.status, questions: prev?.questions || []}));
        setError(null); 
        setIsLoading(false);
        setHasStarted(true);
        return;
      } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error starting quiz:', error);
            setError('Error connecting to the server.');
            setQuizData(null);
            setIsLoading(false);
            return;
          }
      }
    }

  useEffect(() => {
    const fetchQuizData = async () => {
      const quizId = await GenerateQuiz(); // Wait for GenerateQuiz to finish
      if (quizId) {
        await GetQuiz(quizId); // Only call if GenerateQuiz was successful
      }
    };
    fetchQuizData();
  }, []);

  if (isLoading) return <LoadingSpinner/>;
  if (error) return <p>Error loading quiz: {error}</p>;

  if (!hasStarted) {
    return (
      <div className="start-page">
        <h1>Welcome to the Quiz!</h1>
        <p>Topic: {topic}</p>
        <button onClick={() => startQuiz()}>Start Quiz</button>
      </div>
    );
  }
  return quizData ? <Quiz quizData={quizData} /> : <p>No data available</p>;
}

export default QuizComponent;