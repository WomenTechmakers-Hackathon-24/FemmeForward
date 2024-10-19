// src/Homepage.tsx
import React from 'react';
import { useAuth } from './AuthContext.tsx';

const Homepage: React.FC = () => {
  const { user, logout } = useAuth();

  if (!user) {
    return <div>Loading...</div>; // You can show a loading state or redirect
  }
  
  return (
    <div>
      <h1>Welcome, {user.displayName}!</h1>
      <button onClick={logout}>Log out</button>
    </div>
  );
};

export default Homepage;
