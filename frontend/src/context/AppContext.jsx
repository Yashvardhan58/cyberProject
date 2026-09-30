import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [selectedAlertId, setSelectedAlertId] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Mobile off-canvas drawer open/close
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false); // Desktop compact/expanded

  const triggerRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  const toggleSidebarCollapse = () => {
    setIsSidebarCollapsed((prev) => !prev);
  };

  return (
    <AppContext.Provider
      value={{
        selectedAlertId,
        setSelectedAlertId,
        refreshTrigger,
        triggerRefresh,
        isSidebarOpen,
        setIsSidebarOpen,
        isSidebarCollapsed,
        setIsSidebarCollapsed,
        toggleSidebar,
        closeSidebar,
        toggleSidebarCollapse,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
