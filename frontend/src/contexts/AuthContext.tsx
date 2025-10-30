/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, ReactNode } from 'react';
import apiClient from '../services/api';

interface User {
  id: string;
  username: string;
  role: string;
  organizationId: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const login = async (username: string, password: string) => {
    try {
      const response = await apiClient.login({ username, password });

      // Set token in API client
      apiClient.setToken(response.access_token);

      // Store token and user info
      setToken(response.access_token);
      setUser({
        id: response.user_id,
        username,
        role: response.role,
        organizationId: response.organization_id,
      });
    } catch (error) {
      // Clear any existing auth state on login failure
      apiClient.setToken(null);
      setToken(null);
      setUser(null);
      throw error;
    }
  };

  const logout = () => {
    apiClient.setToken(null);
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: !!user && !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
