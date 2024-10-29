// src/Homepage.tsx
import React from 'react';
import { useAuth } from './AuthContext.tsx';

const Homepage: React.FC = () => {
  const { userData, logout } = useAuth();

  if (!userData) {
    return <div>Loading...</div>; // You can show a loading state or redirect
  }
  
  return (
    <div>
      <h1>Welcome, {userData.name}!</h1>
      <button className="button" onClick={logout}>Log out</button>
    </div>
  );
};

export default Homepage;
