import React, { useEffect, useState } from 'react';
import { HiOutlineBookOpen, HiOutlineUsers, HiOutlineDocumentText, HiOutlineSpeakerWave } from 'react-icons/hi2';
import { useAuth } from '../../context/AuthContext';
import { useDashboardRefresh } from '../../context/DashboardContext';
import DashboardLayout from '../../layouts/DashboardLayout';
import './Lecturer.css';

function LecturerDashboard() {
    const { user } = useAuth();
    const { refreshKey } = useDashboardRefresh();
    const [loading, setLoading] = useState(true);

    const stats = {
        courses: 4,
        students: 186,
        pendingResults: 42,
        announcements: 7
    };

    useEffect(() => {
        setLoading(false);
    }, []);

    return (
        <DashboardLayout userRole="lecturer">
            <div className="lecturer-page">

                <div className="lecturer-header">
                    <h1>Lecturer Dashboard</h1>
                </div>

                {loading ? (
                    <div className="ad-loading">
                        Loading...
                    </div>
                ) : (
                    <>
                        <div className="lecturer-hero">
                            <h2>
                                Welcome, {user?.first_name} {user?.last_name}
                            </h2>

                            <p>
                                Manage courses, students and results from one place.
                            </p>
                        </div>

                        <div className="lecturer-stats-grid">

                            <div className="lecturer-stat-card">
                                <HiOutlineBookOpen />
                                <h3>{stats.courses}</h3>
                                <p>Courses</p>
                            </div>

                            <div className="lecturer-stat-card">
                                <HiOutlineUsers />
                                <h3>{stats.students}</h3>
                                <p>Students</p>
                            </div>

                            <div className="lecturer-stat-card">
                                <HiOutlineDocumentText />
                                <h3>{stats.pendingResults}</h3>
                                <p>Pending Results</p>
                            </div>

                            <div className="lecturer-stat-card">
                                <HiOutlineSpeakerWave />
                                <h3>{stats.announcements}</h3>
                                <p>Announcements</p>
                            </div>

                        </div>

                        <div className="lecturer-card">
                            <h3>Recent Activities</h3>

                            <table className="lecturer-table">
                                <thead>
                                    <tr>
                                        <th>Activity</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    <tr>
                                        <td>Uploaded CSC401 Results</td>
                                        <td>Today</td>
                                    </tr>

                                    <tr>
                                        <td>Viewed Student List</td>
                                        <td>Yesterday</td>
                                    </tr>

                                    <tr>
                                        <td>Created Announcement</td>
                                        <td>2 days ago</td>
                                    </tr>
                                </tbody>
                            </table>

                        </div>

                    </>
                )}

            </div>
        </DashboardLayout>
    );
}

export default LecturerDashboard;