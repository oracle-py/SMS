import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingSpinner from '../../components/dashboard/LoadingSpinner';
import ErrorMessage from '../../components/dashboard/ErrorMessage';
import studentService from '../../services/studentService';
import './StudentDashboard.css';

function StudentDashboard() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await studentService.getDashboard();
      setDashboardData(response);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Get student initials for avatar
  const getInitials = (name) => {
    if (!name) return user?.username?.charAt(0).toUpperCase() || 'S';
    return name.split(' ').map(n => n.charAt(0)).join('').toUpperCase().slice(0, 2);
  };

  // Get grade badge class
  const getGradeBadgeClass = (grade) => {
    if (!grade) return 'default';
    const g = grade.toUpperCase();
    if (g === 'A') return 'a';
    if (g === 'B') return 'b';
    if (g === 'C') return 'c';
    if (g === 'D') return 'd';
    if (g === 'F') return 'f';
    return 'default';
  };

  // Get progress bar class based on value
  const getProgressClass = (value, max) => {
    const percentage = (value / max) * 100;
    if (percentage >= 70) return 'success';
    if (percentage >= 50) return 'warning';
    return 'danger';
  };

  if (loading) {
    return (
      <DashboardLayout userRole="student">
        <div className="dashboard-container">
          {/* Skeleton Loading */}
          <div className="welcome-section">
            <div className="skeleton skeleton-avatar"></div>
            <div className="welcome-content">
              <div className="skeleton skeleton-text" style={{ width: '200px' }}></div>
              <div className="skeleton skeleton-text-sm"></div>
            </div>
          </div>
          <div className="skeleton skeleton-hero"></div>
          <div className="profile-card">
            <div className="skeleton skeleton-text" style={{ width: '150px' }}></div>
            <div className="profile-info-grid">
              <div className="skeleton skeleton-text"></div>
              <div className="skeleton skeleton-text"></div>
              <div className="skeleton skeleton-text"></div>
            </div>
          </div>
          <div className="stats-grid">
            <div className="skeleton skeleton-card"></div>
            <div className="skeleton skeleton-card"></div>
            <div className="skeleton skeleton-card"></div>
            <div className="skeleton skeleton-card"></div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout userRole="student">
        <ErrorMessage 
          message={error} 
          onRetry={fetchDashboardData}
        />
      </DashboardLayout>
    );
  }

  const studentName = dashboardData?.student_info?.name || user?.username || 'Student';
  const academicStanding = dashboardData?.academic_standing || 'Not Available';
  const cgpa = dashboardData?.cgpa || 0;
  const attendance = dashboardData?.attendance_percentage || 0;

  return (
    <DashboardLayout userRole="student">
      <div className="dashboard-container">
        {/* Welcome Section */}
        <div className="welcome-section">
          <div className="avatar">
            {getInitials(studentName)}
          </div>
          <div className="welcome-content">
            <h1>Welcome back, {studentName}</h1>
            <p>Academic Standing: {academicStanding}</p>
          </div>
        </div>

        {/* Hero Card */}
        <div className="hero-card">
          <div className="hero-card-content">
            <div className="hero-metric">
              <div className="hero-metric-value">{cgpa.toFixed(2)}</div>
              <div className="hero-metric-label">CGPA</div>
            </div>
            <div className="hero-metric">
              <div className="hero-metric-value">{academicStanding}</div>
              <div className="hero-metric-label">Standing</div>
            </div>
            <div className="hero-metric">
              <div className="hero-metric-value">{attendance.toFixed(1)}%</div>
              <div className="hero-metric-label">Attendance</div>
            </div>
          </div>
        </div>

        {/* Profile Card */}
        <div className="profile-card">
          <h2>Student Profile</h2>
          <div className="profile-info-grid">
            <div className="profile-info-item">
              <span className="profile-info-label">Full Name</span>
              <span className="profile-info-value">{studentName}</span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Matric Number</span>
              <span className="profile-info-value">{dashboardData?.student_info?.matric_number || 'N/A'}</span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Level</span>
              <span className="profile-info-value">{dashboardData?.student_info?.level || 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <h3 className="section-title">Quick Actions</h3>
        <div className="quick-actions-grid">
          <div className="action-card">
            <div className="action-card-icon">📊</div>
            <h4 className="action-card-title">View Results</h4>
          </div>
          <div className="action-card">
            <div className="action-card-icon">📅</div>
            <h4 className="action-card-title">Attendance Records</h4>
          </div>
          <div className="action-card">
            <div className="action-card-icon">📚</div>
            <h4 className="action-card-title">Registered Courses</h4>
          </div>
          <div className="action-card">
            <div className="action-card-icon">👤</div>
            <h4 className="action-card-title">Academic Profile</h4>
          </div>
        </div>

        {/* Statistics Section */}
        <h3 className="section-title">Academic Statistics</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-card-icon">📊</div>
            <div className="stat-card-value">{cgpa.toFixed(2)}</div>
            <div className="stat-card-label">CGPA</div>
            <div className="progress-section">
              <div className="progress-label">
                <span>Progress to 5.0</span>
                <span>{((cgpa / 5.0) * 100).toFixed(0)}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className={`progress-fill ${getProgressClass(cgpa, 5.0)}`}
                  style={{ width: `${(cgpa / 5.0) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-icon">🎓</div>
            <div className="stat-card-value">{academicStanding}</div>
            <div className="stat-card-label">Academic Standing</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-icon">📅</div>
            <div className="stat-card-value">{attendance.toFixed(1)}%</div>
            <div className="stat-card-label">Attendance</div>
            <div className="progress-section">
              <div className="progress-label">
                <span>Attendance Rate</span>
                <span>{attendance.toFixed(0)}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className={`progress-fill ${getProgressClass(attendance, 100)}`}
                  style={{ width: `${attendance}%` }}
                ></div>
              </div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-icon">⚠️</div>
            <div className="stat-card-value">{dashboardData?.carryover_count || 0}</div>
            <div className="stat-card-label">Carryovers</div>
          </div>
        </div>

        {/* Recent Results Section */}
        <h3 className="section-title">Recent Results</h3>
        {dashboardData?.recent_results && dashboardData.recent_results.length > 0 ? (
          <div className="results-card">
            <div className="results-table-container">
              <table className="results-table">
                <thead>
                  <tr>
                    <th>Course</th>
                    <th>Grade</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.recent_results.map((result, index) => (
                    <tr key={index}>
                      <td>{result.course_name || 'N/A'}</td>
                      <td>
                        <span className={`grade-badge ${getGradeBadgeClass(result.grade)}`}>
                          {result.grade || 'N/A'}
                        </span>
                      </td>
                      <td>{result.score || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">📝</div>
            <h3 className="empty-state-title">No Recent Results</h3>
            <p className="empty-state-description">Your recent academic results will appear here once available.</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default StudentDashboard;
