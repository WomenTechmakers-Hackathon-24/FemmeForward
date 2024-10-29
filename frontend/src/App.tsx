import React from 'react';
import { useAuth, AuthProvider } from './AuthContext';
import Homepage from './Homepage';
import Index from './Index';
import Registration from './components/Registration';
import LoadingSpinner from './components/LoadingSpinner';

const App: React.FC = () => {
  const { user, userData, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (userData && userData.isRegistered) {
    return <Homepage />;
  }

  if (user ) {
    return <Registration />;
  }

  return <Index />;
};

// Wrap your app with the AuthProvider
const RootApp = () => (
  <AuthProvider>
    <App />
  </AuthProvider>
);

export default RootApp;