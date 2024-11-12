// src/Index.tsx
import React from 'react';
import { useAuth } from './AuthContext.tsx';
import LoginComponent from './components/LoginComponent.tsx';

const Index: React.FC = () => {
  const { error } = useAuth();
  
  return (
    <div className="centered-container">
      <div className="logo-container">
        <img src="/FemmeForward.png" alt="Logo" className="logo" />
        <h1 className="title">Femme Forward</h1>
      </div>
      <LoginComponent />
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
};

export default Index;
