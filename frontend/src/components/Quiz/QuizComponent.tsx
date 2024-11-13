import api from '@/api/axios';
import { QuizData } from '@/types/quiz';
import axios from 'axios';
import { useEffect, useState } from 'react';
import Quiz from './Quiz';
import LoadingSpinner from '../ui/LoadingSpinner';
import { Card } from '../ui/card';
import { Button } from '../ui/button';

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

  if (isLoading) return <LoadingSpinner message="Generating Quiz"/>;
  if (error) return <p>Error loading quiz: {error}</p>;

  if (!hasStarted) {
    return (
      <div className="flex justify-center items-center min-h-screen py-8">
        <Card className="p-6 max-w-sm w-full bg-white shadow-lg rounded-lg text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-4">Welcome to the Quiz!</h1>
          <p className="text-lg text-gray-600 mb-6">Topic: <span className="font-semibold text-blue-500">{topic}</span></p>
          <Button onClick={() => startQuiz()} className="w-full py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition duration-200">
            Start Quiz
          </Button>
        </Card>
      </div>
    );
  }

  return quizData ? <Quiz quizData={quizData} /> : <p>No data available</p>;
}

export default QuizComponent;