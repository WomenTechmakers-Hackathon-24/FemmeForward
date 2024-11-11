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

  const GenerateQuiz = async () => {
      setIsLoading(true);
      try {
        const response = await api.post(`/generate_quiz`, {
          topic: topic, 
          num_questions: 5
        });
        setQuizData(response.data);
        setError(null); 
        return;
      } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error getting quiz data', error);
            setError('Error connecting to the server.');
            setQuizData(null);
            return;
          }
      }
      finally {
        setIsLoading(false);
      }
    }

    const GetQuiz = async () => {
      setIsLoading(true);
      try {
        const response = await api.post(`/get_quiz`, {
          quiz_id: quizData?.quiz_id
        });
        setQuizData(response.data);
        setError(null); 
        setIsLoading(false);
        return;
      } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error getting quiz data', error);
            setError('Error connecting to the server.');
            setQuizData(null);
            setIsLoading(false);
            return;
          }
      }
    }

    const startQuiz = async () => {
      try {
        const response = await api.post(`/start_quiz`, {
          quiz_id: quizData?.quiz_id
        });
        setQuizData(response.data);
        setError(null); 
        setIsLoading(false);
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
      setHasStarted(true);
    }

  useEffect(() => {
    const fetchQuizData = async () => {
      await GenerateQuiz(); // Wait for GenerateQuiz to finish
      if (quizData?.quiz_id) { // Ensure quizData is available before calling GetQuiz
        GetQuiz();
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