import { useState, useEffect, useCallback } from 'react';
import { authApi } from '../../../shared/api';
import { User } from '../../../entities/user/model';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authApi.login(email, password);
      const { user: userData, token } = response.data;
      

      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      const userEntity = User.fromApiResponse(userData);
      setUser(userEntity);
      
      return { success: true, user: userEntity };
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (email, password, name) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authApi.register(email, password, name);
      const { user: userData, token } = response.data;
      

      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      const userEntity = User.fromApiResponse(userData);
      setUser(userEntity);
      
      return { success: true, user: userEntity };
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Registration failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setError(null);
  }, []);

  const verifyToken = useCallback(async () => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (!token || !storedUser) {
      setLoading(false);
      return false;
    }

    try {
      await authApi.verifyToken();
      const userData = JSON.parse(storedUser);
      const userEntity = User.fromApiResponse(userData);
      setUser(userEntity);
      setLoading(false);
      return true;
    } catch (err) {
      console.error('Token verification failed:', err);
      logout();
      setLoading(false);
      return false;
    }
  }, [logout]);

  useEffect(() => {
    verifyToken();
  }, [verifyToken]);

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    verifyToken,
    isAuthenticated: Boolean(user),
  };
}; 