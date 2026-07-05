import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useDashboardRefresh } from '../../context/DashboardContext';
import DashboardLayout from '../../layouts/DashboardLayout';
import studentService from '../../services/studentService';
import './student.css';

/* -- Icon Components ---------------------------------- */
const IconTrendingUp = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
  </svg>
);

const IconCalendar = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
    <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
  </svg>
);

const IconAward = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/>
  </svg>
);

const IconAlertCircle = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
    <line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);

const IconFileText = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
  </svg>
);

const IconBook = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
  </svg>
);

const IconUser = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
);

const IconInbox = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/>
    <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>
  </svg>
);

/* -- Helper Functions -------------------------------- */
const getInitials = (name, username) => {
  if (!name) return username?.charAt(0).toUpperCase() || 'S';
  const parts = name.trim().split(' ');
  return parts.length >= 2
    ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
    : parts[0][0].toUpperCase();
};

const gradeBadgeClass = (grade) => {
  if (!grade) return 'sp-badge sp-badge-default';
  const g = grade.toUpperCase();
  if (g.startsWith('A')) return 'sp-badge sp-badge-a';
  if (g.startsWith('B')) return 'sp-badge sp-badge-b';
  if (g.startsWith('C')) return 'sp-badge sp-badge-c';
  return 'sp-badge sp-badge-d';
};

/* -- Skeleton Component ------------------------------- */
function DashboardSkeleton() {
  return (
    <div className="sp-page">
      <div className="sp-skeleton" style={{ height: 130, borderRadius: 18, marginBottom: 24 }} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 16, marginBottom: 24 }}>
        {[1,2,3,4].map(i => <div key={i} className="sp-skeleton" style={{ height: 110, borderRadius: 14 }} />)}
      </div>
      <div className="sp-skeleton" style={{ height: 90, borderRadius: 14, marginBottom: 24 }} />
      <div className="sp-skeleton" style={{ height: 220, borderRadius: 14 }} />
    </div>
  );
}

/* -- Main Component ----------------------------------- */
function StudentDashboard() {
  const { user } = useAuth();
  const { refreshKey, refreshDashboard } = useDashboardRefresh();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await studentService.getDashboard();
        setData(res);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    })();
  }, [refreshKey]); // Refetch when refreshKey changes

  if (loading) {
    return (
      <DashboardLayout userRole="student">
        <DashboardSkeleton />
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout userRole="student">
        <div className="sp-empty">
          <div className="sp-empty-icon red"><IconAlertCircle /></div>
          <h3>Something went wrong</h3>
          <p>{error}</p>
          <button className="sp-filter-clear" style={{ marginTop: 16 }} onClick={() => window.location.reload()}>
            Try again
          </button>
        </div>
      </DashboardLayout>
    );
  }

  const studentName = data?.student_info?.name || user?.username || 'Student';
  const standing = data?.academic_standing || 'N/A';
  const cgpa = data?.cgpa || 0;
  const attendance = data?.attendance_percentage || 0;
  const carryovers = data?.carryover_count || 0;

  return (
    <DashboardLayout userRole="student">
      <div className="sp-page">

        {/* Hero Banner */}
        <div className="hub-hero">
          <div className="hero-blob hero-blob-1"></div>
          <div className="hero-blob hero-blob-2"></div>
          <div className="hero-blob hero-blob-3"></div>

          <div className="hub-hero-left">
            <p className="hub-greeting">? Good Morning,</p>
            <h1 className="hub-name">{studentName}</h1>
            <p className="hub-programme">
              {data?.student_info?.department || "N/A"} • {data?.student_info?.level || "N/A"}
            </p>
            <div className="hub-standing">
              <span className="standing-dot"></span>
              {standing}
            </div>
            <p className="hub-message">
              Keep pushing towards academic excellence. Every semester counts.
            </p>
          </div>

          <div className="hub-hero-right">
            <div className="hero-mini-card">
              <span>CGPA</span>
              <h2>{cgpa.toFixed(2)}</h2>
            </div>
            <div className="hero-mini-card">
              <span>Attendance</span>
              <h2>{attendance.toFixed(0)}%</h2>
            </div>
            <div className="hero-mini-card">
              <span>Credits</span>
              <h2>{data?.student_info?.credits || 0}</h2>
            </div>
            <div className="hero-mini-card">
              <span>Session</span>
              <h2>{data?.current_session || "2025/2026"}</h2>
            </div>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="hub-kpi-grid">
          {/* CGPA */}
          <div className="hub-kpi-card">
            <div className="hub-kpi-top">
              <div className="hub-kpi-icon blue">
                <IconTrendingUp />
              </div>
              <span className="hub-kpi-tag">Academic</span>
            </div>
            <h2>{cgpa.toFixed(2)}</h2>
            <p>Cumulative GPA</p>
            <div className="hub-kpi-footer">
              <span className="hub-positive">? Excellent Progress</span>
            </div>
          </div>

          {/* Attendance */}
          <div className="hub-kpi-card">
            <div className="hub-kpi-top">
              <div className="hub-kpi-icon green">
                <IconCalendar />
              </div>
              <span className="hub-kpi-tag">This Semester</span>
            </div>
            <h2>{attendance.toFixed(0)}%</h2>
            <p>Attendance Rate</p>
            <div className="hub-meter">
              <div className="hub-meter-fill green" style={{ width: `${attendance}%` }} />
            </div>
          </div>

          {/* Standing */}
          <div className="hub-kpi-card">
            <div className="hub-kpi-top">
              <div className="hub-kpi-icon amber">
                <IconAward />
              </div>
            </div>
            <h2>{standing}</h2>
            <p>Academic Standing</p>
            <div className="hub-kpi-footer">
              Ranked among top performers.
            </div>
          </div>

          {/* Carryovers */}
          <div className="hub-kpi-card">
            <div className="hub-kpi-top">
              <div className={`hub-kpi-icon ${carryovers > 0 ? 'red' : 'green'}`}>
                <IconAlertCircle />
              </div>
            </div>
            <h2>{carryovers}</h2>
            <p>Outstanding Courses</p>
            <div className="hub-kpi-footer">
              {carryovers === 0 ? 'Excellent record' : 'Requires attention'}
            </div>
          </div>
        </div>

        {/* Academic Overview */}
        {/* ================= ACADEMIC OVERVIEW ================= */}

<div className="hub-overview-grid">

    {/* Academic Health */}

    <div className="hub-health-card">

        <div className="hub-card-header">

            <h3>Academic Health</h3>

            <span>This Semester</span>

        </div>

        <div className="hub-health-circle">

            <svg viewBox="0 0 120 120">

                <circle
                    className="circle-bg"
                    cx="60"
                    cy="60"
                    r="50"
                />

                <circle
                    className="circle-progress"
                    cx="60"
                    cy="60"
                    r="50"
                    strokeDasharray="314"
                    strokeDashoffset={314 - ((attendance * 314) / 100)}
                />

            </svg>

            <div className="hub-health-score">

                {attendance.toFixed(0)}

                <small>%</small>

            </div>

        </div>

        <div className="hub-health-status">

            {attendance >= 75
                ? "Excellent Attendance"
                : attendance >= 60
                ? "Good Standing"
                : "Needs Improvement"}

        </div>

        <div className="hub-health-bars">

            <div>

                <label>CGPA</label>

                <progress value={cgpa} max="5"></progress>

            </div>

            <div>

                <label>Attendance</label>

                <progress value={attendance} max="100"></progress>

            </div>

            <div>

                <label>Carryovers</label>

                <progress value={carryovers === 0 ? 100 : 25} max="100"></progress>

            </div>

        </div>

    </div>

    {/* Student Profile */}

    <div className="hub-profile-card">

        <div className="hub-profile-top">

            <div className="hub-avatar">

                {getInitials(studentName)}

            </div>

            <div>

                <h3>{studentName}</h3>

                <p>

                    {data?.student_info?.department || "N/A"}

                </p>

            </div>

        </div>

        <div className="hub-profile-grid">

            <div>

                <span>Matric Number</span>

                <strong>

                    {data?.student_info?.matric_number || "--"}

                </strong>

            </div>

            <div>

                <span>Level</span>

                <strong>

                    {data?.student_info?.level || "--"}

                </strong>

            </div>

            <div>

                <span>Faculty</span>

                <strong>

                    {data?.student_info?.faculty || "N/A"}

                </strong>

            </div>

            <div>

                <span>Status</span>

                <strong className="status-active">

                    Active

                </strong>

            </div>

        </div>

    </div>

</div>

        {/* ================= BOTTOM GRID ================= */}

<div className="hub-bottom-grid">

    {/* Recent Results */}

    <div className="hub-panel">

        <div className="hub-panel-header">

            <h3>Recent Results</h3>

            <button>View All</button>

        </div>

        {

            data?.recent_results?.length

            ?

            data.recent_results.map((course,index)=>(

                <div
                    key={index}
                    className="hub-result-item"
                >

                    <div>

                        <h4>

                            {course.course_name}

                        </h4>

                        <span>

                            {course.course_code}

                        </span>

                    </div>

                    <div className="hub-result-right">

                        <div className={gradeBadgeClass(course.grade)}>

                            {course.grade}

                        </div>

                        <strong>

                            {course.score}

                        </strong>

                    </div>

                </div>

            ))

            :

            <div className="hub-empty">

                No recent results available.

            </div>

        }

    </div>

    {/* Upcoming Schedule */}

    <div className="hub-panel">

        <div className="hub-panel-header">

            <h3>Upcoming Schedule</h3>

        </div>

        <div className="hub-schedule-item">

            <div className="hub-time">

                10:00

            </div>

            <div>

                <strong>

                    Software Engineering

                </strong>

                <p>

                    Today

                </p>

            </div>

        </div>

        <div className="hub-schedule-item">

            <div className="hub-time">

                08:00

            </div>

            <div>

                <strong>

                    Control Systems

                </strong>

                <p>

                    Tomorrow

                </p>

            </div>

        </div>

        <div className="hub-schedule-item">

            <div className="hub-time">

                13:00

            </div>

            <div>

                <strong>

                    Engineering Mathematics

                </strong>

                <p>

                    Thursday

                </p>

            </div>

        </div>

    </div>

</div>

{/* ================= ANNOUNCEMENTS ================= */}

<div className="hub-announcements">

    <div className="hub-panel-header">

        <h3>Latest Announcements</h3>

        <button>See All</button>

    </div>

    <div className="announcement-item">

        <div className="announcement-icon">

            📢

        </div>

        <div>

            <strong>

                Course Registration closes this Friday

            </strong>

            <p>

                Complete registration before the deadline.

            </p>

        </div>

    </div>

    <div className="announcement-item">

        <div className="announcement-icon">

            🎓

        </div>

        <div>

            <strong>

                SIWES Orientation

            </strong>

            <p>

                Monday • Engineering Auditorium

            </p>

        </div>

    </div>

    <div className="announcement-item">

        <div className="announcement-icon">

            📝

        </div>

        <div>

            <strong>

                CBT Examination Timetable Released

            </strong>

            <p>

                View your examination schedule.

            </p>

        </div>

    </div>

</div>

{/* ================= STUDENT INSIGHTS ================= */}

<div className="hub-insights-grid">

    {/* Graduation Progress */}

    <div className="hub-widget">

        <div className="hub-widget-header">

            <h3>Graduation Progress</h3>

            <span>Credits</span>

        </div>

        <h2>

            {data?.student_info?.credits || 94}

        </h2>

        <p>

            Credits Earned

        </p>

        <div className="hub-progress">

            <div

                className="hub-progress-fill"

                style={{

                    width: `${((data?.student_info?.credits || 94) / 140) * 100}%`

                }}

            />

        </div>

        <div className="hub-progress-footer">

            <span>

                {data?.student_info?.credits || 94} / 140

            </span>

            <span>

                {Math.round(((data?.student_info?.credits || 94) / 140) * 100)}%

            </span>

        </div>

    </div>

    {/* Weekly Attendance */}

    <div className="hub-widget">

        <div className="hub-widget-header">

            <h3>Weekly Attendance</h3>

            <span>This Week</span>

        </div>

        <div className="hub-week">

            <div className="day present">

                <span>M</span>

                ✓

            </div>

            <div className="day present">

                <span>T</span>

                ✓

            </div>

            <div className="day present">

                <span>W</span>

                ✓

            </div>

            <div className="day absent">

                <span>T</span>

                ○

            </div>

            <div className="day present">

                <span>F</span>

                ✓

            </div>

        </div>

        <div className="hub-week-summary">

            Attendance this week:

            <strong>

                {" "}

                {attendance.toFixed(0)}%

            </strong>

        </div>

    </div>

    {/* Academic Insight */}

    <div className="hub-widget">

        <div className="hub-widget-header">

            <h3>Academic Insight</h3>

            <span>AI Assistant</span>

        </div>

        <div className="hub-insight-icon">

            💡

        </div>

        <h4>

            {

                cgpa >= 4.5

                    ? "Outstanding Performance"

                    : cgpa >= 3.5

                        ? "Good Progress"

                        : "Needs Improvement"

            }

        </h4>

        <p>

            {

                cgpa >= 4.5

                    ?

                    "Your academic performance has remained consistently excellent. Keep maintaining your attendance and continue submitting assessments on time."

                    :

                    cgpa >= 3.5

                        ?

                        "You are making good progress. Improving attendance and staying consistent can help you reach First Class."

                        :

                        "Focus on improving attendance, completing assignments early, and attending revision sessions."

            }

        </p>

    </div>

</div>

      </div>
    </DashboardLayout>
  );
}

export default StudentDashboard;
