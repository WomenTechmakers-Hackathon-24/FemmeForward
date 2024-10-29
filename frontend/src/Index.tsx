// src/Index.tsx
import React, { useEffect } from 'react';
import { useAuth } from './AuthContext.tsx';
import LoginComponent from './components/LoginComponent.tsx';

const Index: React.FC = () => {
  const { error } = useAuth();
  
  return (
    <div className="centered-container">
      <h1 className="logo">Empowering Women</h1>
      <LoginComponent/>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>  
  );
};

export default Index;
