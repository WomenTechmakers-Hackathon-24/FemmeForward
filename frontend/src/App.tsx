// src/App.tsx
import React from 'react';
import { useAuth, AuthProvider } from './AuthContext.tsx';
import Homepage from './Homepage';
import Index from './Index';

const App: React.FC = () => {
  const auth = useAuth();

  return (
    <div>
      {auth?.user ? <Homepage /> : <Index />}
    </div>
  );
};

// Wrap your app with the AuthProvider
const RootApp = () => (
  <AuthProvider>
    <App />
  </AuthProvider>
);

export default RootApp;
