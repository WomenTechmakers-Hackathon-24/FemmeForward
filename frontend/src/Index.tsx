// src/Index.tsx
import React from 'react';
import { useAuth } from './AuthContext.tsx';

const Index: React.FC = () => {
  const { login } = useAuth();

  return (
    <div>
      <h1>Please log in</h1>
      <button onClick={login}>Log in with Google</button>
    </div>
  );
};

export default Index;
