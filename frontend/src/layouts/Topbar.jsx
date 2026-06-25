import React from 'react';
import { useAuth } from '../context/AuthContext';
import './Topbar.css';

function Topbar({ toggleSidebar }) {
  const { user } = useAuth();

  const fullName =
    user?.first_name && user?.last_name
      ? `${user.first_name} ${user.last_name}`
      : user?.username || 'User';

  const initials = user?.first_name
    ? user.first_name.charAt(0).toUpperCase()
    : user?.username?.charAt(0).toUpperCase() || 'U';

  const roleLabel = {
    student: 'Student',
    parent: 'Parent',
    admin: 'Administrator',
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button
          className="menu-btn"
          onClick={toggleSidebar}
        >
          ☰
        </button>

        <div>
          <h2 className="page-title">
            Dashboard
          </h2>

          <p className="page-subtitle">
            Welcome back
          </p>
        </div>
      </div>

      <div className="topbar-right">
        <button className="notification-btn">
          🔔
        </button>

        <div className="user-profile">
          <div className="user-info">
            <div className="user-name">
              {fullName}
            </div>

            <div className="user-role">
              {roleLabel[user?.role] || 'User'}
            </div>
          </div>

          <div className="user-avatar">
            {initials}
          </div>
        </div>
      </div>
    </header>
  );
}

export default Topbar;