import api from '@/api/axios';
import { QuizData } from '@/types/quiz';
import axios from 'axios';
import { useEffect, useState } from 'react';
import Quiz from './Quiz';
import { mockQuizData } from './MockQuiz';
import LoadingSpinner from '../ui/LoadingSpinner';

interface QuizComponentProps {
  topic: string; // The title of the topic selected for the quiz
}

const QuizComponent: React.FC<QuizComponentProps> = ({topic}) => {
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getQuestions = async () => {
      setIsLoading(true);
      try {
        const response = await api.post(`/generate_quiz`, {
          topic: topic, 
          //tags: tags,
          //age_group: age_group,
          //num_questions: num_questions
        });
        setQuizData(response.data);
        setError(null); 
        setIsLoading(false);
        return;
      } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error checking user registration:', error);
            setError('Error connecting to the server.');
            setQuizData(null);
            setIsLoading(false);
            return;
          }
      }
    }

  useEffect(() => {
    setQuizData(mockQuizData);
    //getQuestions();
  }, []);


  if (isLoading) return <LoadingSpinner/>;
  if (error) return <p>Error loading quiz: {error}</p>;

  return quizData ? <Quiz quizData={quizData} /> : <p>No data available</p>;
}

export default QuizComponent;