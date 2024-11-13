import React, { createContext, useContext, useEffect, useState } from 'react';
import { 
  auth, 
  signInWithPopup, 
  GoogleAuthProvider, 
  signOut, 
  User
} from './firebase';
import {
  setPersistence,
  browserLocalPersistence,
  browserSessionPersistence,
  getAuth
} from 'firebase/auth';
import { UserData, LoadingState } from './types/auth';
import axios from 'axios';
import api from './api/axios';

interface AuthContextProps {
  googleUser: User | null;
  userData: UserData | null;
  loadingStates: LoadingState;
  error: string | null;
  rememberMe: boolean;
  setRememberMe: (remember: boolean) => void;
  setError: (error: string | null) => void;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  completeRegistration: (userData: Partial<UserData>) => Promise<void>;
  updateUserData: (updatedUser: UserData) => void;
}

const AuthContext = createContext<AuthContextProps | null>(null);

const RETRY_DELAYS = [1000, 2000, 4000]; // Exponential backoff delays in ms

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [googleUser, setGoogleUser] = useState<User | null>(null);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loadingStates, setLoadingStates] = useState<LoadingState>({
    auth: false,
    registration: false,
    profileCheck: false
  });
  const [error, setError] = useState<string | null>(null);
  const [rememberMe, setRememberMe] = useState(() => {
    return localStorage.getItem('rememberMe') === 'true';
  });

  useEffect(() => {
    localStorage.setItem('rememberMe', rememberMe.toString());
  }, [rememberMe]);

  const checkUserRegistration = async (user: User, retries = 3) => {
    setLoadingStates(prev => ({ ...prev, profileCheck: true }));
    const auth = getAuth();
    const currentUser = auth.currentUser;

    if (!currentUser) {
      console.error('Error checking user registration:', error);
      setError('Error connecting to the server.');
      setGoogleUser(null);
      setUserData(null);
      return;
    }
    const firebaseIdToken = await currentUser.getIdToken();

    for (let i = 0; i < retries; i++) {
      try {
        const response = await api.post(`/verify-token`, {
          token: firebaseIdToken
        });
        setUserData(response.data.user);
        setError(null); 
        setLoadingStates(prev => ({ ...prev, profileCheck: false }));
        return;
      } catch (error) {
        if (axios.isAxiosError(error)) {
          // Handle 404 (user not found) - this is an expected case for new users
          if (error.response?.status === 404) {
            setError(null);
            setUserData(null);
            setLoadingStates(prev => ({ ...prev, profileCheck: false }));
            return;
          }
          
          // On last retry, handle the error by logging out
          if (i === retries - 1) {
            console.error('Error checking user registration:', error);
            setError('Error connecting to the server.');
            setGoogleUser(null);
            setUserData(null);
            setLoadingStates(({ 
              auth: false, 
              registration: false, 
              profileCheck: false 
            }));
            await logout();
            return;
          }
          
          // Wait before retry using exponential backoff
          await new Promise(resolve => setTimeout(resolve, RETRY_DELAYS[i]));
        }
      }
    }
  };

  const login = async () => {
    setLoadingStates(prev => ({ ...prev, auth: true }));
    setError(null);
    
    try {
      await setPersistence(
        auth, 
        rememberMe ? browserLocalPersistence : browserSessionPersistence
      );

      const result = await signInWithPopup(auth, new GoogleAuthProvider());
      if (result.user) {
        await checkUserRegistration(result.user);
      }
    } catch (error) {
      console.error('Login error:', error);
      
      // Handle specific Google Sign-In errors
      if (error instanceof Error) {
        switch ((error as any).code) {
          case 'auth/popup-closed-by-user':
            setError('Sign-in was cancelled. Please try again.');
            break;
          case 'auth/cancelled-popup-request':
            setError('Another popup is already open. Close it and try again.');
            break;
          case 'auth/network-request-failed':
            setError('Network error. Check your connection and try again.');
            break;
          default:
            setError('Unable to sign in. Please try again later.');
        }
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
      
      setGoogleUser(null);
      setUserData(null);
    } finally {
      setLoadingStates(prev => ({ ...prev, auth: false }));
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
      setUserData(null);
      setGoogleUser(null);
      setError(null);
      setLoadingStates({
        auth: false,
        registration: false,
        profileCheck: false
      });
    } catch (error) {
      console.error('Logout error:', error);
      setError('Logout failed. Please try again.');
    }
  };

  const completeRegistration = async (newUserData: Partial<UserData>) => {
    if (!googleUser) return;

    setLoadingStates(prev => ({ ...prev, registration: true }));
    try {
      const response = await api.post('/register', {
        ...newUserData,
        id: googleUser.uid,
        email: googleUser.email
      });
      
      setUserData(response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('Registration error:', error.response?.data);
        throw new Error(error.response?.data?.message || 'Registration failed');
      }
      throw error;
    } finally {
      setLoadingStates(prev => ({ ...prev, registration: false }));
    }
  };

  const updateUserData = (updatedUser : UserData) => {
    setUserData(updatedUser);
  }

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      try {
        setGoogleUser(user);
        if (user) {
          await checkUserRegistration(user);
        } else {
          setUserData(null);
          setLoadingStates({
            auth: false,
            registration: false,
            profileCheck: false
          });
        }
      } catch (error) {
        console.error('Auth state change error:', error);
        setGoogleUser(null);
        setUserData(null);
        setError('Authentication error occurred.');
        setLoadingStates({
          auth: false,
          registration: false,
          profileCheck: false
        });
      }
    });
  
    return () => unsubscribe();
  }, []);

  return (
    <AuthContext.Provider 
      value={{ 
        googleUser, 
        userData, 
        loadingStates,
        error, 
        rememberMe,
        setRememberMe,
        setError, 
        login, 
        logout, 
        completeRegistration,
        updateUserData
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextProps => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
