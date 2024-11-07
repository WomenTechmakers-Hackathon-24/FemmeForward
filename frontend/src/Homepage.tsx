// src/Homepage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from './AuthContext.tsx';
import api from './api/axios.tsx';
import QuizComponent from './components/Quiz/QuizComponent.tsx';
import LoadingSpinner from './components/ui/LoadingSpinner.tsx';

const Homepage: React.FC = () => {
  const { userData, logout } = useAuth();
  const [loading, setLoading] = useState(false);  // State for loading state

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
  
  return (
    <div>
      <div className="taskbar bg-blue-500 text-white p-4 flex justify-between items-center w-full fixed top-0 left-0">
        <div className="text-lg font-bold">Empowering Women</div> {/* Logo or app name on the left */}
        <div className="flex items-center space-x-4"> {/* Added space between elements */}
          <h1 className="text-lg">Welcome, {userData.name}!</h1>
          <button className="button bg-red-500 hover:bg-red-600 text-white p-2 rounded" onClick={logout}>Log out</button>
        </div>
      </div>
      <div className="mt-16"> {/* Added top margin to avoid overlap */}
        <QuizComponent />
      </div>
    </div>
  );
};

export default Homepage;
