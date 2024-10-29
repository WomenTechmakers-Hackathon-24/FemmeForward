// src/Index.tsx
import React, { useEffect } from 'react';
import { useAuth } from './AuthContext.tsx';

const Index: React.FC = () => {
  const { login, error, setError } = useAuth();

  useEffect(() => {
    setError(null); // Clear the error state when the component mounts
  }, [setError]);
  
  return (
    <div className="centered-container">
      <h1 className="logo">Empowering Women</h1>
      <button className="button" onClick={login}>Log in with Google</button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>  
  );
};

export default Index;
