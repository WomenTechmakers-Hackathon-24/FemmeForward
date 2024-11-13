// src/App.tsx
import React from 'react';
import { useAuth, AuthProvider } from './AuthContext';
import Homepage from './Homepage';
import Index from './Index';
import Registration from './components/Registration';
import LoadingSpinner from './components/ui/LoadingSpinner';

const App: React.FC = () => {
  const { googleUser, userData, loadingStates, error } = useAuth();

  // Show loading spinner only if we're actually loading something
  if (loadingStates.auth || (loadingStates.profileCheck && !userData)) {
    return <LoadingSpinner />;
  }

  // If there's an error or no user, show the index page
  if (error || !googleUser) {
    return <Index />;
  }

  // If user is registered, show homepage
  if (userData) {
    return <Homepage />;
  }

  // If user exists but isn't registered, show registration
  if (googleUser) {
    return <Registration />;
  }

  // Fallback to index
  return <Index />;
};


// Wrap your app with the AuthProvider
const RootApp = () => (
  <AuthProvider>
    <App />
  </AuthProvider>
);

export default RootApp;