import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import DashboardLayout from "../../layouts/DashboardLayout";
import "./admin.css";

import RegisterStudentDrawer from "./components/RegisterStudentDrawer";
import RegisterLecturerDrawer from "./components/RegisterLecturerDrawer";
import CreateCourseDrawer from "./components/CreateCourseDrawer";
import ResultsReviewDrawer from "./components/ReviewResultsDrawer";

import {
    HiOutlineAcademicCap,
    HiOutlineUsers,
    HiOutlineBookOpen,
    HiOutlineClipboardDocumentList,
    HiOutlineUserPlus,
    HiOutlinePlusCircle,
    HiOutlineDocumentArrowUp,
    HiOutlineClock,
    HiOutlineArrowTrendingUp,
    HiOutlineBuildingLibrary,
    HiOutlineBellAlert,
    HiOutlineChartBar
} from "react-icons/hi2";

function AdminDashboard() {

    const { user } = useAuth();

    const [drawer, setDrawer] = useState(null);
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(false);

    const openDrawer = (name) => setDrawer(name);
    const closeDrawer = () => setDrawer(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    useEffect(() => {
        // Refetch data when component gains focus (user returns to tab)
        const handleVisibilityChange = () => {
            if (!document.hidden) {
                fetchDashboardData();
            }
        };
        
        document.addEventListener('visibilitychange', handleVisibilityChange);
        return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
    }, []);

    const fetchDashboardData = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/dashboard/admin/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                console.log('Dashboard data:', data);
                setDashboardData(data.data);
            } else {
                console.error('Dashboard API error:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const statistics = dashboardData?.statistics ? [
        {
            title: "Students",
            value: dashboardData.statistics.students.total,
            icon: <HiOutlineAcademicCap />,
            color: "blue",
            change: dashboardData.statistics.students.change_this_week
        },
        {
            title: "Lecturers",
            value: dashboardData.statistics.lecturers.total,
            icon: <HiOutlineUsers />,
            color: "green",
            change: dashboardData.statistics.lecturers.change_this_week
        },
        {
            title: "Parents",
            value: dashboardData.statistics.parents.total,
            icon: <HiOutlineUsers />,
            color: "purple",
            change: dashboardData.statistics.parents.change_this_week
        },
        {
            title: "Courses",
            value: dashboardData.statistics.courses.total,
            icon: <HiOutlineBookOpen />,
            color: "orange",
            change: dashboardData.statistics.courses.change_this_week
        }
    ] : [
        {
            title: "Students",
            value: "0",
            icon: <HiOutlineAcademicCap />,
            color: "blue",
            change: "Loading..."
        },
        {
            title: "Lecturers",
            value: "0",
            icon: <HiOutlineUsers />,
            color: "green",
            change: "Loading..."
        },
        {
            title: "Parents",
            value: "0",
            icon: <HiOutlineUsers />,
            color: "purple",
            change: "Loading..."
        },
        {
            title: "Courses",
            value: "0",
            icon: <HiOutlineBookOpen />,
            color: "orange",
            change: "Loading..."
        }
    ];

    const quickActions = [

        {

            title:"Register Student",

            description:"Create a new student profile.",

            icon:<HiOutlineUserPlus/>,

            color:"blue",

            action:()=>openDrawer("student")

        },

        {

            title:"Register Lecturer",

            description:"Create lecturer accounts.",

            icon:<HiOutlineAcademicCap/>,

            color:"green",

            action:()=>openDrawer("lecturer")

        },

        {

            title:"Create Course",

            description:"Add courses for departments.",

            icon:<HiOutlinePlusCircle/>,

            color:"orange",

            action:()=>openDrawer("course")

        },

        {

            title:"Review Results",

            description:"Approve submitted grades.",

            icon:<HiOutlineDocumentArrowUp/>,

            color:"purple",

            action:()=>openDrawer("results")

        }

    ];

    const recentRegistrations = dashboardData?.recent_registrations || [];

    const pendingResults = dashboardData?.pending_results || [];

    const activities = dashboardData?.recent_activities?.map(a => a.description) || [];

    return (

        <DashboardLayout userRole="admin">

            <div className="ad-page">

                {/* HERO */}

                <section className="ad-hero">

                    <div className="ad-hero-left">

                        <span className="ad-hero-badge">

                            University Management Portal

                        </span>

                        <h1>

                            Welcome back,

                            {" "}

                            {user?.first_name || user?.username || "Administrator"}

                        </h1>

                        <p>

                            Manage students, lecturers, parents, courses and academic records from one unified dashboard.

                        </p>

                    </div>

                    <div className="ad-hero-right">

                        <div className="hero-stat">

                            <HiOutlineArrowTrendingUp />

                            <div>

                                <h2>96%</h2>

                                <span>System Performance</span>

                            </div>

                        </div>

                        <div className="hero-stat">

                            <HiOutlineBuildingLibrary />

                            <div>

                                <h2>{dashboardData?.statistics?.departments?.total || 0}</h2>

                                <span>Departments</span>

                            </div>

                        </div>

                    </div>

                </section>

                {/* STATISTICS */}

                <section className="ad-statistics">

                    {

                        statistics.map((item,index)=>(

                            <div

                                key={index}

                                className={`ad-stat-card ${item.color}`}

                            >

                                <div className="ad-stat-icon">

                                    {item.icon}

                                </div>

                                <div className="ad-stat-info">

                                    <span>

                                        {item.title}

                                    </span>

                                    <h2>

                                        {item.value}

                                    </h2>

                                    <small>

                                        {item.change}

                                    </small>

                                </div>

                            </div>

                        ))

                    }

                </section>

                                {/* MAIN GRID */}

                <div className="ad-main-grid">

                    {/* QUICK ACTIONS */}

                    <section className="ad-card">

                        <div className="ad-card-header">

                            <div>

                                <h2>

                                    Quick Actions

                                </h2>

                                <p>

                                    Frequently used administrative operations.

                                </p>

                            </div>

                        </div>

                        <div className="ad-actions-grid">

                            {

                                quickActions.map((action,index)=>(

                                    <button

                                        key={index}

                                        className={`ad-action-card ${action.color}`}

                                        onClick={action.action}

                                    >

                                        <div className="ad-action-icon">

                                            {action.icon}

                                        </div>

                                        <div className="ad-action-content">

                                            <h3>

                                                {action.title}

                                            </h3>

                                            <p>

                                                {action.description}

                                            </p>

                                        </div>

                                    </button>

                                ))

                            }

                        </div>

                    </section>

                    {/* RECENT REGISTRATIONS */}

                    <section className="ad-card">

                        <div className="ad-card-header">

                            <div>

                                <h2>

                                    Recent Registrations

                                </h2>

                                <p>

                                    Newly added students.

                                </p>

                            </div>

                        </div>

                        <div className="ad-registration-list">

                            {

                                recentRegistrations.map((student,index)=>(

                                    <div

                                        key={index}

                                        className="ad-registration-item"

                                    >

                                        <div className="ad-avatar">

                                            {

                                                student.name

                                                .split(" ")

                                                .map(word=>word[0])

                                                .join("")

                                                .substring(0,2)

                                            }

                                        </div>

                                        <div className="ad-registration-info">

                                            <h4>

                                                {student.name}

                                            </h4>

                                            <p>

                                                {student.department}

                                            </p>

                                        </div>

                                        <span>

                                            {student.level}

                                        </span>

                                    </div>

                                ))

                            }

                        </div>

                    </section>

                </div>

                {/* LOWER GRID */}

                <div className="ad-lower-grid">

                    {/* RESULTS */}

                    <section className="ad-card">

                        <div className="ad-card-header">

                            <div>

                                <h2>

                                    Pending Result Approval

                                </h2>

                                <p>

                                    Lecturer submissions awaiting review.

                                </p>

                            </div>

                        </div>

                        <div className="ad-results-list">

                            {

                                pendingResults.map((result,index)=>(

                                    <div

                                        key={index}

                                        className="ad-result-item"

                                    >

                                        <div className="ad-result-icon">

                                            <HiOutlineClipboardDocumentList/>

                                        </div>

                                        <div className="ad-result-info">

                                            <h4>

                                                {result.course}

                                            </h4>

                                            <p>

                                                {result.lecturer}

                                            </p>

                                        </div>

                                        <div className="ad-result-meta">

                                            <span>

                                                {result.students} Students

                                            </span>

                                            <button>

                                                Review

                                            </button>

                                        </div>

                                    </div>

                                ))

                            }

                        </div>

                    </section>

                    {/* ACTIVITY */}

                    <section className="ad-card">

                        <div className="ad-card-header">

                            <div>

                                <h2>

                                    Recent Activity

                                </h2>

                                <p>

                                    Latest actions across the platform.

                                </p>

                            </div>

                        </div>

                        <div className="ad-activity-list">

                            {

                                activities.map((activity,index)=>(

                                    <div

                                        key={index}

                                        className="ad-activity-item"

                                    >

                                        <div className="ad-activity-dot"/>

                                        <span>

                                            {activity}

                                        </span>

                                    </div>

                                ))

                            }

                        </div>

                    </section>

                </div>

                {/* DRAWER PLACEHOLDER */}

                <RegisterStudentDrawer
                    open={drawer === "student"}
                    onClose={closeDrawer}
                />

                <RegisterLecturerDrawer
                    open={drawer === "lecturer"}
                    onClose={closeDrawer}
                />

                <CreateCourseDrawer
                    open={drawer === "course"}
                    onClose={closeDrawer}
                />

                <ResultsReviewDrawer
                    open={drawer === "results"}
                    onClose={closeDrawer}
/>

            </div>

        </DashboardLayout>

    );

}

export default AdminDashboard;