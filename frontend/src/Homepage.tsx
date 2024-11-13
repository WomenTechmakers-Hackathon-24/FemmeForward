// src/Homepage.tsx
import React, { useState } from 'react';
import QuizComponent from './components/Quiz/QuizComponent.tsx';
import TaskbarComponent from './components/TaskbarComponent.tsx';
import TopicComponent from './components/Topic/TopicComponent.tsx';
import ProfileComponent from './components/ProfileComponent.tsx';

const Homepage: React.FC = () => {
  const [currentView, setCurrentView] = useState<'topics' | 'quiz' | 'profile' | null>('topics');
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null); // Track selected topic for quiz

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
