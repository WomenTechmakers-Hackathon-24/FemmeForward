// src/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { auth, signInWithPopup, GoogleAuthProvider, signOut, User } from './firebase.tsx';

interface AuthContextProps {
  user: User | null;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextProps | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User|null>(null);

  // Google login
  const login = () => signInWithPopup(auth, new GoogleAuthProvider()).catch((error) => console.error(error));

  // Logout
  const logout = () => signOut(auth).catch((error) => console.error(error));

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      setUser(user);
    });
    return () => unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
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
