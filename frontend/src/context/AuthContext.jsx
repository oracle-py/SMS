import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('access_token');
    const refresh = localStorage.getItem('refresh_token');
    const userData = localStorage.getItem('user_data');
    
    if (token && refresh && userData) {
      setAccessToken(token);
      setRefreshToken(refresh);
      setUser(JSON.parse(userData));
      setAuthenticated(true);
      // Verify token is still valid by fetching current user
      getCurrentUser();
    }
    
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login/', {
        username: email,
        password: password,
      });
      
      const { access, refresh, user: userData } = response.data;
      
      setAccessToken(access);
      setRefreshToken(refresh);
      setUser(userData);
      setAuthenticated(true);
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const logout = async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      await api.post('/auth/logout/', {
        refresh_token: refresh,
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setAccessToken(null);
      setRefreshToken(null);
      setAuthenticated(false);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_data');
      localStorage.removeItem('sidebarOpen'); // Clear sidebar state on logout
    }
  };

  const getCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me/');
      const userData = response.data.data;
      
      setUser(userData);
      setAuthenticated(true);
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      return userData;
    } catch (error) {
      console.error('Get current user error:', error);
      // If token is invalid, try to refresh it
      if (error.response?.status === 401) {
        const newToken = await refreshAccessToken();
        if (newToken) {
          // Retry with new token
          try {
            const response = await api.get('/auth/me/');
            const userData = response.data.data;
            setUser(userData);
            setAuthenticated(true);
            localStorage.setItem('user_data', JSON.stringify(userData));
            return userData;
          } catch (retryError) {
            console.error('Retry get current user error:', retryError);
            await logout();
          }
        } else {
          await logout();
        }
      }
      return null;
    }
  };

  const refreshAccessToken = async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      const response = await api.post('/auth/refresh/', {
        refresh: refresh,
      });
      
      const { access } = response.data;
      
      setAccessToken(access);
      localStorage.setItem('access_token', access);
      
      return access;
    } catch (error) {
      console.error('Refresh token error:', error);
      await logout();
      return null;
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      accessToken, 
      refreshToken, 
      loading, 
      authenticated,
      login, 
      logout, 
      getCurrentUser,
      refreshAccessToken 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
