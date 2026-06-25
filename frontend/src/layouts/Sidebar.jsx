import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Sidebar.css';

function Sidebar({ isOpen, userRole, toggleSidebar }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const studentLinks = [
    {
      path: '/student/dashboard',
      label: 'Dashboard',
      icon: '📊',
    },
    {
      path: '/student/results',
      label: 'Results',
      icon: '📄',
    },
    {
      path: '/student/attendance',
      label: 'Attendance',
      icon: '📅',
    },
  ];

  const parentLinks = [
    {
      path: '/parent/dashboard',
      label: 'Dashboard',
      icon: '🏠',
    },
    {
      path: '/parent/wards',
      label: 'Ward Details',
      icon: '👨‍🎓',
    },
  ];

  const adminLinks = [
    {
      path: '/admin/dashboard',
      label: 'Dashboard',
      icon: '⚙️',
    },
  ];

  const getLinks = () => {
    switch (userRole) {
      case 'student':
        return studentLinks;
      case 'parent':
        return parentLinks;
      case 'admin':
        return adminLinks;
      default:
        return [];
    }
  };

  const links = getLinks();

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-brand">
        <div className="brand-logo">🎓</div>

        {isOpen && (
          <div className="brand-content">
            <h3>SMS Portal</h3>
            <p>Student Monitoring</p>
          </div>
        )}

        <button
          className="collapse-btn"
          onClick={toggleSidebar}
        >
          {isOpen ? '←' : '→'}
        </button>
      </div>

      <nav className="sidebar-nav">
        {links.map((link) => (
          <div
            key={link.path}
            className={`sidebar-link ${
              location.pathname === link.path
                ? 'active'
                : ''
            }`}
            onClick={() => navigate(link.path)}
          >
            <span className="sidebar-icon">
              {link.icon}
            </span>

            {isOpen && (
              <span className="sidebar-label">
                {link.label}
              </span>
            )}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button
          className="logout-btn"
          onClick={handleLogout}
        >
          <span>🚪</span>

          {isOpen && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;