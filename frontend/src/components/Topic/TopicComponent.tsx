import axios from 'axios';
import { useEffect, useState } from 'react';
import LoadingSpinner from '../ui/LoadingSpinner';
import { TopicList } from '@/types/topic';
import api from '@/api/axios';
import { Badge } from "@/components/ui/badge";
import { defaultColor, tagColorMap } from '@/types/tags';

interface TopicComponentProps {
    onTopicClick: (topic: string) => void;
};

const TopicComponent: React.FC<TopicComponentProps> = ({ onTopicClick }) => {
  const [topics, setTopics] = useState<TopicList | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getColorClasses = (tag: string) => {
    return tagColorMap[tag] || defaultColor;
  };
  
  const getTopics = async () => {
      setIsLoading(true);
      try {
        const response = await api.get(`/topics`);
        setTopics(response.data);
        setError(null); 
        setIsLoading(false);
        return;
      } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error checking user registration:', error);
            setError('Error connecting to the server.');
            setTopics(null);
            setIsLoading(false);
            return;
          }
      }
    }

  useEffect(() => {
    getTopics();
  }, []);


  if (isLoading) return <LoadingSpinner/>;
  if (error) return <p>Error loading quiz: {error}</p>;

  return (
    <div>
      {topics ? (
        <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {topics.topics.map((topic, index) => (
          <div key={index} className="border rounded-lg shadow-md p-4 bg-white" onClick={() => onTopicClick(topic.title)}>
            <h3 className="text-lg font-semibold mb-2">{topic.title}</h3>
            <div className="flex flex-wrap gap-2">
              {topic.tags.map((tag, i) => (
                <Badge key={i} className={`text-sm ${getColorClasses(tag)}`}>
                {tag}
              </Badge>
              ))}
            </div>
          </div>
        ))}
      </div>
      ) : (
        <p>No posts available.</p>
      )}
    </div>);
}

export default TopicComponent;