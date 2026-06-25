import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import './DashboardLayout.css';


function DashboardLayout({ children, userRole }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="dashboard-layout">
      <Sidebar
        isOpen={sidebarOpen}
        userRole={userRole}
        toggleSidebar={toggleSidebar}
      />

      <div
        className={`dashboard-main ${
          sidebarOpen ? 'sidebar-open' : 'sidebar-closed'
        }`}
      >
        <Topbar
          toggleSidebar={toggleSidebar}
        />

        <main className="dashboard-content">
          {children}
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;