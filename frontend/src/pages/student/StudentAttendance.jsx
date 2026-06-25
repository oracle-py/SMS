import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingSpinner from '../../components/dashboard/LoadingSpinner';
import ErrorMessage from '../../components/dashboard/ErrorMessage';
import AttendanceTable from '../../components/attendance/AttendanceTable';
import StatCard from '../../components/dashboard/StatCard';
import studentService from '../../services/studentService';

function StudentAttendance() {
  const [attendanceData, setAttendanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [courseFilter, setCourseFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('all');

  const fetchAttendance = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await studentService.getAttendance();
      setAttendanceData(response);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttendance();
  }, []);

  // Get unique courses and statuses from records
  const courses = [...new Set((attendanceData?.data?.records || []).map(r => r.course_code).filter(Boolean))];
  const statuses = [...new Set((attendanceData?.data?.records || []).map(r => r.status).filter(Boolean))];

  // Filter records based on search, status, course, and date
  const filteredRecords = (attendanceData?.data?.records || []).filter(record => {
    // Search filter
    const matchesSearch = searchTerm === '' || 
      (record.course_code && record.course_code.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (record.course_title && record.course_title.toLowerCase().includes(searchTerm.toLowerCase()));
    
    // Status filter
    const matchesStatus = statusFilter === '' || record.status === statusFilter;
    
    // Course filter
    const matchesCourse = courseFilter === '' || record.course_code === courseFilter;
    
    // Date filter
    let matchesDate = true;
    if (dateFilter !== 'all' && record.date) {
      const recordDate = new Date(record.date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (dateFilter === 'today') {
        matchesDate = recordDate.toDateString() === today.toDateString();
      } else if (dateFilter === 'last7days') {
        const sevenDaysAgo = new Date(today);
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        matchesDate = recordDate >= sevenDaysAgo && recordDate <= today;
      } else if (dateFilter === 'last30days') {
        const thirtyDaysAgo = new Date(today);
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        matchesDate = recordDate >= thirtyDaysAgo && recordDate <= today;
      }
    }
    
    return matchesSearch && matchesStatus && matchesCourse && matchesDate;
  });

  if (loading) {
    return (
      <DashboardLayout userRole="student">
        <LoadingSpinner />
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout userRole="student">
        <ErrorMessage 
          message={error} 
          onRetry={fetchAttendance}
        />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout userRole="student">
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '20px' }}>
          Attendance Records
        </h1>

        {/* Summary Section */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '24px' }}>
          <StatCard
            title="Attendance Percentage"
            value={`${attendanceData?.data?.attendance_percentage?.toFixed(1) || '0.0'}%`}
            icon="📊"
          />
          <StatCard
            title="Total Records"
            value={attendanceData?.data?.total_records || 0}
            icon="📝"
          />
          <StatCard
            title="Present"
            value={attendanceData?.data?.present_records || 0}
            icon="✅"
          />
          <StatCard
            title="Absent"
            value={attendanceData?.data?.absent_records || 0}
            icon="❌"
          />
        </div>

        {/* Filters and Search */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e5e7eb',
        }}>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {/* Search */}
            <div style={{ flex: 1, minWidth: '200px' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', color: '#6b7280', marginBottom: '8px' }}>
                Search
              </label>
              <input
                type="text"
                placeholder="Course code or title..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                }}
              />
            </div>

            {/* Status Filter */}
            {statuses.length > 0 && (
              <div style={{ minWidth: '150px' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', color: '#6b7280', marginBottom: '8px' }}>
                  Status
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                  }}
                >
                  <option value="">All Statuses</option>
                  {statuses.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Course Filter */}
            {courses.length > 0 && (
              <div style={{ minWidth: '150px' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', color: '#6b7280', marginBottom: '8px' }}>
                  Course
                </label>
                <select
                  value={courseFilter}
                  onChange={(e) => setCourseFilter(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                  }}
                >
                  <option value="">All Courses</option>
                  {courses.map(course => (
                    <option key={course} value={course}>{course}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Date Filter */}
            <div style={{ minWidth: '150px' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', color: '#6b7280', marginBottom: '8px' }}>
                Date Range
              </label>
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                }}
              >
                <option value="all">All Records</option>
                <option value="today">Today</option>
                <option value="last7days">Last 7 Days</option>
                <option value="last30days">Last 30 Days</option>
              </select>
            </div>

            {/* Clear Filters */}
            {(searchTerm || statusFilter || courseFilter || dateFilter !== 'all') && (
              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setStatusFilter('');
                    setCourseFilter('');
                    setDateFilter('all');
                  }}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#6b7280',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                  }}
                >
                  Clear Filters
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Records Count */}
        <div style={{ marginBottom: '16px', color: '#6b7280', fontSize: '0.875rem' }}>
          Showing {filteredRecords.length} of {attendanceData?.data?.records?.length || 0} records
        </div>

        {/* Attendance Table */}
        <AttendanceTable records={filteredRecords} loading={loading} />
      </div>
    </DashboardLayout>
  );
}

export default StudentAttendance;
