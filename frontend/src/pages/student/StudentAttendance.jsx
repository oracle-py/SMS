import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import AttendanceTable from '../../components/attendance/AttendanceTable';
import studentService from '../../services/studentService';
import './student.css';

/* ── Icons ──────────────────────────────────────────── */
const IconCheck = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);
const IconX = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);
const IconCalendar = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
    <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
  </svg>
);
const IconTrendingUp = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
  </svg>
);
const IconAlertCircle = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
    <line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);

/* ── Date helpers ───────────────────────────────────── */
const filterByDate = (record, range) => {
  if (range === 'all' || !record.date) return true;
  const d     = new Date(record.date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (range === 'today')      return d.toDateString() === today.toDateString();
  if (range === 'last7days')  { const t = new Date(today); t.setDate(t.getDate() - 7);  return d >= t && d <= today; }
  if (range === 'last30days') { const t = new Date(today); t.setDate(t.getDate() - 30); return d >= t && d <= today; }
  return true;
};

/* ── Component ──────────────────────────────────────── */
function StudentAttendance() {
  const [attendanceData, setAttendanceData] = useState(null);
  const [loading,        setLoading]        = useState(true);
  const [error,          setError]          = useState(null);
  const [searchTerm,     setSearchTerm]     = useState('');
  const [statusFilter,   setStatusFilter]   = useState('');
  const [courseFilter,   setCourseFilter]   = useState('');
  const [dateFilter,     setDateFilter]     = useState('all');

  const fetchAttendance = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await studentService.getAttendance();
      setAttendanceData(res);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAttendance(); }, []);

  const records  = attendanceData?.data?.records || [];
  const courses  = [...new Set(records.map(r => r.course_code).filter(Boolean))];
  const statuses = [...new Set(records.map(r => r.status).filter(Boolean))];

  const filtered = records.filter(r => {
    const q = searchTerm.toLowerCase();
    const matchSearch  = !q || r.course_code?.toLowerCase().includes(q) || r.course_title?.toLowerCase().includes(q);
    const matchStatus  = !statusFilter || r.status === statusFilter;
    const matchCourse  = !courseFilter || r.course_code === courseFilter;
    const matchDate    = filterByDate(r, dateFilter);
    return matchSearch && matchStatus && matchCourse && matchDate;
  });

  const hasFilters   = searchTerm || statusFilter || courseFilter || dateFilter !== 'all';
  const clearFilters = () => { setSearchTerm(''); setStatusFilter(''); setCourseFilter(''); setDateFilter('all'); };

  const pct         = attendanceData?.data?.attendance_percentage || 0;
  const total       = attendanceData?.data?.total_records   || 0;
  const present     = attendanceData?.data?.present_records || 0;
  const absent      = attendanceData?.data?.absent_records  || 0;

  const progressClass = pct >= 70 ? 'success' : pct >= 50 ? 'warning' : 'danger';

  if (loading) return (
    <DashboardLayout userRole="student">
      <div className="sp-page">
        <div className="sp-skeleton" style={{ height: 36, width: 220, marginBottom: 24, borderRadius: 8 }} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(190px,1fr))', gap: 16, marginBottom: 24 }}>
          {[1,2,3,4].map(i => <div key={i} className="sp-skeleton" style={{ height: 110, borderRadius: 14 }} />)}
        </div>
        <div className="sp-skeleton" style={{ height: 80, borderRadius: 14, marginBottom: 20 }} />
        <div className="sp-skeleton" style={{ height: 300, borderRadius: 14 }} />
      </div>
    </DashboardLayout>
  );

  if (error) return (
    <DashboardLayout userRole="student">
      <div className="sp-empty" style={{ marginTop: 40 }}>
        <div className="sp-empty-icon" style={{ background: 'var(--red-light)', color: 'var(--red)' }}>
          <IconAlertCircle />
        </div>
        <h3>Couldn't load attendance</h3>
        <p>{error}</p>
        <button className="sp-filter-clear" style={{ marginTop: 16 }} onClick={fetchAttendance}>Retry</button>
      </div>
    </DashboardLayout>
  );

  return (
    <DashboardLayout userRole="student">
      <div className="sp-page">

        <div className="sp-page-header">
          <h1>Attendance Records</h1>
          <p>Track your class attendance across all courses</p>
        </div>

        {/* Stat Cards */}
        <div className="sp-stats-grid">
          <div className="sp-stat-card">
            <div className="sp-stat-icon"><IconTrendingUp /></div>
            <div className="sp-stat-value">{pct.toFixed(1)}%</div>
            <div className="sp-stat-label">Overall Attendance</div>
            <div className="sp-progress-wrap">
              <div className="sp-progress-row"><span>Rate</span><span>{pct.toFixed(0)}%</span></div>
              <div className="sp-progress-track">
                <div className={`sp-progress-fill ${progressClass}`} style={{ width: `${Math.min(pct, 100)}%` }} />
              </div>
            </div>
          </div>

          <div className="sp-stat-card">
            <div className="sp-stat-icon"><IconCalendar /></div>
            <div className="sp-stat-value">{total}</div>
            <div className="sp-stat-label">Total Classes</div>
          </div>

          <div className="sp-stat-card">
            <div className="sp-stat-icon green"><IconCheck /></div>
            <div className="sp-stat-value">{present}</div>
            <div className="sp-stat-label">Present</div>
          </div>

          <div className="sp-stat-card">
            <div className="sp-stat-icon red"><IconX /></div>
            <div className="sp-stat-value">{absent}</div>
            <div className="sp-stat-label">Absent</div>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="sp-filter-bar">
          <div className="sp-filter-group grow">
            <label className="sp-filter-label">Search</label>
            <input
              className="sp-filter-input"
              type="text"
              placeholder="Course code or title…"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>

          {statuses.length > 0 && (
            <div className="sp-filter-group fixed">
              <label className="sp-filter-label">Status</label>
              <select className="sp-filter-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
                <option value="">All Statuses</option>
                {statuses.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          )}

          {courses.length > 0 && (
            <div className="sp-filter-group fixed">
              <label className="sp-filter-label">Course</label>
              <select className="sp-filter-select" value={courseFilter} onChange={e => setCourseFilter(e.target.value)}>
                <option value="">All Courses</option>
                {courses.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          )}

          <div className="sp-filter-group fixed">
            <label className="sp-filter-label">Date Range</label>
            <select className="sp-filter-select" value={dateFilter} onChange={e => setDateFilter(e.target.value)}>
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="last7days">Last 7 Days</option>
              <option value="last30days">Last 30 Days</option>
            </select>
          </div>

          {hasFilters && (
            <button className="sp-filter-clear" onClick={clearFilters}>Clear filters</button>
          )}
        </div>

        <p className="sp-results-count">
          Showing <strong>{filtered.length}</strong> of <strong>{records.length}</strong> records
        </p>

        {filtered.length > 0 ? (
          <AttendanceTable records={filtered} loading={false} />
        ) : (
          <div className="sp-empty">
            <div className="sp-empty-icon"><IconCalendar /></div>
            <h3>No records found</h3>
            <p>{hasFilters ? 'Try adjusting your filters.' : 'Your attendance records will appear here.'}</p>
          </div>
        )}

      </div>
    </DashboardLayout>
  );
}

export default StudentAttendance;
