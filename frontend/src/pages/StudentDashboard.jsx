import React from 'react';
import { useAuth } from '../context/AuthContext';

function StudentDashboard() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    window.location.href = '/';
  };

  return (
    <div>
      <h1>Student Dashboard</h1>
      <p>Role: Student</p>
      <p>Welcome, {user?.username || 'Student'}</p>
      <button 
        onClick={handleLogout}
        style={{
          padding: '10px 20px',
          backgroundColor: '#dc3545',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          marginTop: '20px'
        }}
      >
        Logout
      </button>
    </div>
  );
}

export default StudentDashboard;
