import React from "react";
import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../layouts/DashboardLayout";

import {
    HiOutlineAcademicCap,
    HiOutlineUser,
    HiOutlineChartBar,
    HiOutlineClipboardDocumentCheck,
    HiOutlineBanknotes,
    HiOutlineArrowTrendingUp,
    HiOutlineEnvelope,
    HiOutlinePhone,
    HiOutlineCalendarDays,
    HiOutlineBookOpen
} from "react-icons/hi2";

import "./Parent.css";

function ParentDashboard() {
    const { user } = useAuth();
    const { refreshKey } = useDashboardRefresh();

    // Temporary data until API integration
   const student = {
    name: "John Doe",
    matricNo: "UJ/FNS/20/001",
    department: "Mechanical Engineering",
    faculty: "Faculty of Engineering",
    level: "400 Level",
    semester: "Second Semester",
    session: "2025/2026",

    cgpa: "4.21",
    attendance: 92,
    fees: "Paid",

    email: "john.doe@school.edu",
    phone: "+234 812 345 6789",

    results: [
        {
            course: "MEE401",
            title: "Machine Design",
            score: 82,
            grade: "A"
        },
        {
            course: "MEE403",
            title: "Thermodynamics II",
            score: 74,
            grade: "B"
        },
        {
            course: "MEE405",
            title: "Fluid Mechanics",
            score: 67,
            grade: "B"
        }
    ]
};

    return (
    <DashboardLayout>

        <div className="parent-page">

            {/* ================= HERO ================= */}

            <section className="parent-hero">

                <div className="parent-hero-pattern"></div>

                <div className="parent-hero-content">

                    <span className="parent-badge">
                        <HiOutlineAcademicCap />
                        Parent Portal
                    </span>

                    <h1>
                        Welcome back,
                        <br />
                        {user?.first_name || user?.username}
                    </h1>

                    <p>
                        Monitor your child's academic performance,
                        attendance, fee status and semester activities
                        from one dashboard.
                    </p>

                    <div className="parent-hero-stats">

                        <div>

                            <span>Student</span>

                            <strong>{student.name}</strong>

                        </div>

                        <div>

                            <span>Session</span>

                            <strong>{student.session}</strong>

                        </div>

                        <div>

                            <span>Current Level</span>

                            <strong>{student.level}</strong>

                        </div>

                    </div>

                </div>

            </section>

            {/* ================= TOP CARDS ================= */}

            <section className="parent-summary-grid">

                <div className="parent-summary-card">

                    <div className="summary-icon blue">

                        <HiOutlineChartBar />

                    </div>

                    <div>

                        <span>Current CGPA</span>

                        <h2>{student.cgpa}</h2>

                    </div>

                </div>

                <div className="parent-summary-card">

                    <div className="summary-icon green">

                        <HiOutlineClipboardDocumentCheck />

                    </div>

                    <div>

                        <span>Attendance</span>

                        <h2>{student.attendance}%</h2>

                    </div>

                </div>

                <div className="parent-summary-card">

                    <div className="summary-icon gold">

                        <HiOutlineBanknotes />

                    </div>

                    <div>

                        <span>School Fees</span>

                        <h2>{student.fees}</h2>

                    </div>

                </div>

                <div className="parent-summary-card">

                    <div className="summary-icon purple">

                        <HiOutlineArrowTrendingUp />

                    </div>

                    <div>

                        <span>Performance</span>

                        <h2>Excellent</h2>

                    </div>

                </div>

            </section>

                        {/* ================= MAIN GRID ================= */}

            <section className="parent-dashboard-grid">

                {/* LEFT COLUMN */}

                <div className="parent-left-column">

                    {/* STUDENT PROFILE */}

                    <div className="parent-panel">

                        <div className="panel-title">

                            <HiOutlineUser />

                            <h3>Student Profile</h3>

                        </div>

                        <div className="student-profile">

                            <div className="student-avatar">

                                {student.name
                                    .split(" ")
                                    .map(n => n[0])
                                    .join("")}

                            </div>

                            <div>

                                <h2>{student.name}</h2>

                                <span>{student.matricNo}</span>

                            </div>

                        </div>

                        <div className="info-grid">

                            <div>

                                <label>Faculty</label>

                                <strong>{student.faculty}</strong>

                            </div>

                            <div>

                                <label>Department</label>

                                <strong>{student.department}</strong>

                            </div>

                            <div>

                                <label>Current Level</label>

                                <strong>{student.level}</strong>

                            </div>

                            <div>

                                <label>Semester</label>

                                <strong>{student.semester}</strong>

                            </div>

                        </div>

                    </div>

                    {/* CONTACT */}

                    <div className="parent-panel">

                        <div className="panel-title">

                            <HiOutlineEnvelope />

                            <h3>Contact Information</h3>

                        </div>

                        <div className="contact-list">

                            <div className="contact-item">

                                <HiOutlineEnvelope />

                                <div>

                                    <span>Email</span>

                                    <strong>{student.email}</strong>

                                </div>

                            </div>

                            <div className="contact-item">

                                <HiOutlinePhone />

                                <div>

                                    <span>Phone</span>

                                    <strong>{student.phone}</strong>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

                {/* RIGHT COLUMN */}

                <div className="parent-right-column">

                    {/* ATTENDANCE */}

                    <div className="parent-panel attendance-panel">

                        <div className="panel-title">

                            <HiOutlineClipboardDocumentCheck />

                            <h3>Attendance Overview</h3>

                        </div>

                        <div className="attendance-circle">

                            <svg>

                                <circle
                                    cx="70"
                                    cy="70"
                                    r="55"
                                ></circle>

                                <circle
                                    className="progress"
                                    cx="70"
                                    cy="70"
                                    r="55"
                                    style={{
                                        strokeDashoffset:
                                            345 -
                                            (345 * student.attendance) / 100
                                    }}
                                ></circle>

                            </svg>

                            <div className="attendance-value">

                                {student.attendance}%

                            </div>

                        </div>

                        <p>

                            Attendance this semester.

                            Excellent consistency.

                        </p>

                    </div>

                    {/* SESSION */}

                    <div className="parent-panel">

                        <div className="panel-title">

                            <HiOutlineCalendarDays />

                            <h3>Academic Session</h3>

                        </div>

                        <div className="info-grid">

                            <div>

                                <label>Session</label>

                                <strong>{student.session}</strong>

                            </div>

                            <div>

                                <label>Semester</label>

                                <strong>{student.semester}</strong>

                            </div>

                            <div>

                                <label>Status</label>

                                <strong>Active</strong>

                            </div>

                            <div>

                                <label>Registration</label>

                                <strong>Completed</strong>

                            </div>

                        </div>

                    </div>

                </div>

            </section>

                        {/* ================= RESULTS ================= */}

            <section className="parent-panel">

                <div className="panel-header">

                    <div className="panel-title">

                        <HiOutlineBookOpen />

                        <h3>Recent Academic Results</h3>

                    </div>

                    <span className="panel-subtitle">
                        Latest published semester results
                    </span>

                </div>

                <div className="results-table-wrapper">

                    <table className="results-table">

                        <thead>

                            <tr>

                                <th>Course Code</th>

                                <th>Course Title</th>

                                <th>Score</th>

                                <th>Grade</th>

                                <th>Status</th>

                            </tr>

                        </thead>

                        <tbody>

                            {student.results.map((course) => (

                                <tr key={course.course}>

                                    <td>

                                        <span className="course-code">

                                            {course.course}

                                        </span>

                                    </td>

                                    <td>

                                        {course.title}

                                    </td>

                                    <td>

                                        <strong>

                                            {course.score}%

                                        </strong>

                                    </td>

                                    <td>

                                        <span
                                            className={`grade-badge grade-${course.grade}`}
                                        >

                                            {course.grade}

                                        </span>

                                    </td>

                                    <td>

                                        <span className="status-pill">

                                            Passed

                                        </span>

                                    </td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            </section>

        </div>

    </DashboardLayout>

);
}

export default ParentDashboard;