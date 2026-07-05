import { createContext, useContext, useState, useCallback } from 'react';

const DashboardContext = createContext(null);

export const DashboardProvider = ({ children }) => {
  const [refreshKey, setRefreshKey] = useState(0);

  const refreshDashboard = useCallback(() => {
    setRefreshKey(prev => prev + 1);
  }, []);

  return (
    <DashboardContext.Provider value={{ refreshKey, refreshDashboard }}>
      {children}
    </DashboardContext.Provider>
  );
};

export const useDashboardRefresh = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboardRefresh must be used within a DashboardProvider');
  }
  return context;
};
