// src/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { auth, signInWithPopup, GoogleAuthProvider, signOut, User } from './firebase';
import { UserData } from './types/auth';
import axios from 'axios';
import api from './api/axios';

interface AuthContextProps {
  user: User | null;
  userData: UserData | null;
  isLoading: boolean;
  error: string | null;
  setError: (error: string | null) => void; // Add setError function
  login: () => void;
  logout: () => void;
  completeRegistration: (userData: Partial<UserData>) => Promise<void>;
}

const AuthContext = createContext<AuthContextProps | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkUserRegistration = async (user: User) => {
    try {
      const response = await api.get(`/profile?email=${user.email}`);
      setUserData(response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {  // This line needs the axios import
        // Handle 404 (user not found) or other errors
        const isNotFound = error.response?.status === 404;
        setError(null);
        // Set minimal user data for unregistered or error cases
        setUserData({
          id: user.uid,
          email: user.email || '',
          name: user.displayName || '',
          birthdate: '',
          isRegistered: false
        });

        if (!isNotFound) {
          console.error('Error checking user registration:', error);
          setError('Error connecting to the server.');
          setUser(null);
          logout();
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async () => {
    try {
      const result = await signInWithPopup(auth, new GoogleAuthProvider());
      if (result.user) {
        setError(null);
        setUser(result.user);  // Set user state immediately
        await checkUserRegistration(result.user);
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Login failed. Please try again.');
      setIsLoading(false);
      setUser(null);
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
      setUserData(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const completeRegistration = async (newUserData: Partial<UserData>) => {
    if (!user) return;

    try {
      const response = await api.post('/users', {
        ...newUserData,
        id: user.uid,
        email: user.email,
        isRegistered: true,
      });
      
      setUserData(response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {  // This line needs the axios import
        console.error('Registration error:', error.response?.data);
        throw new Error(error.response?.data?.message || 'Registration failed');
      }
      throw error;
    }
  };

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      setUser(user);
      if (user) {
        await checkUserRegistration(user);
      } else {
        setUserData(null);
        setIsLoading(false);
      }
    });

    return () => unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ user, userData, isLoading, error, setError, login, logout, completeRegistration }}>
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