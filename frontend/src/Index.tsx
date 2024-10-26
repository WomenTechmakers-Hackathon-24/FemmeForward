// src/Index.tsx
import React from 'react';
import { useAuth } from './AuthContext.tsx';

const Index: React.FC = () => {
  const { login } = useAuth();

  return (
    <div className="centered-container">
      <h1 className="logo">Empowering Women</h1>
      <button className="button" onClick={login}>Log in with Google</button>
    </div>
  );
};

export default Index;
