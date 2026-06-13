import { createContext, useState, useEffect } from 'react';
import api from '../services/api';
import toast from 'react-hot-toast';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      setUser({ email: 'user@example.com' }); // Basic mock user for context
    }
    setLoading(false);
  }, [token]);

  const login = async (email, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      const res = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      setToken(res.data.access_token);
      localStorage.setItem('token', res.data.access_token);
      setUser({ email });
      toast.success('Successfully logged in!');
    } catch (error) {
      console.error(error.response?.data);
      toast.error(error.response?.data?.detail || 'Failed to login');
      throw error;
    }
  };

  const register = async (email, password) => {
    try {
      await api.post('/auth/register', { email, password });
      toast.success('Registration successful! Logging you in...');
      await login(email, password);
    } catch (error) {
      console.error(error.response?.data);
      toast.error(error.response?.data?.detail || 'Failed to register');
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
