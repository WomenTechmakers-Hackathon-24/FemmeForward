// src/Homepage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from './AuthContext.tsx';
import api from './api/axios.tsx';
import QuizComponent from './components/Quiz/QuizComponent.tsx';
import LoadingSpinner from './components/ui/LoadingSpinner.tsx';
import TaskbarComponent from './components/TaskbarComponent.tsx';
import TopicComponent from './components/Topic/TopicComponent.tsx';
import ProfileComponent from './components/ProfileComponent.tsx';

const Homepage: React.FC = () => {
  const { userData } = useAuth();
  const [loading, setLoading] = useState(false);  // State for loading state
  const [currentView, setCurrentView] = useState<'topics' | 'quiz' | 'profile' | null>('topics');
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null); // Track selected topic for quiz

  const GetContent = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/content`);
      console.log(response);
      //setApiData(data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    //GetContent();
  }, []); // Empty dependency array ensures it only runs once

  if (loading || !userData) {
    return <LoadingSpinner />;
  }
  

  // Handlers to switch views
  const handleTopicClick = (topic: string) => {
    setSelectedTopic(topic);
    setCurrentView('quiz');
  };

  const handleProfileClick = () => {
    setCurrentView('profile');
  };

  const handleBack = () => {
    setCurrentView('topics');
    setSelectedTopic(null);
  };

  return (
    <div>
      <TaskbarComponent onBack={handleBack} onProfileClick={handleProfileClick}  />
      <div className="mt-32"> {/* Added top margin to avoid overlap */}
      <div>
      {/* Conditional rendering of views */}
      {currentView === 'topics' && (
        <TopicComponent onTopicClick={handleTopicClick} />
      )}
      {currentView === 'quiz' && selectedTopic && (
        <QuizComponent topic={selectedTopic} />
      )}
      {currentView === 'profile' && <ProfileComponent />}
    </div>
      </div>
    </div>
  );
};

export default Homepage;
