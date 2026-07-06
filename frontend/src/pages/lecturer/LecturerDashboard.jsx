import React, { useEffect, useState } from 'react';
import { HiOutlineBookOpen, HiOutlineUsers, HiOutlineDocumentText, HiOutlineSpeakerWave } from 'react-icons/hi2';
import { useAuth } from '../../context/AuthContext';
import { useDashboardRefresh } from '../../context/DashboardContext';
import DashboardLayout from '../../layouts/DashboardLayout';
import api from '../../api/axios';
import './Lecturer.css';

function LecturerDashboard() {
    const { user } = useAuth();
    const { refreshKey } = useDashboardRefresh();
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        courses: 0,
        students: 0,
        pendingResults: 0,
        announcements: 0
    });
    const [recentActivities, setRecentActivities] = useState([]);

    useEffect(() => {
        fetchDashboardData();
    }, [refreshKey]);

    const fetchDashboardData = async () => {
        setLoading(true);
        try {
            // Get current lecturer's profile
            const userResponse = await api.get('/auth/me/');
            const lecturerId = userResponse.data.profile?.id;
            
            // Fetch lecturer's courses
            let courses = [];
            if (lecturerId) {
                const lecturerResponse = await api.get(`/lecturers/${lecturerId}/`);
                courses = lecturerResponse.data.courses || [];
            }
            
            // Fetch lecturer's students (total students across all assigned courses)
            let totalStudents = 0;
            for (const course of courses) {
                try {
                    const studentsResponse = await api.get('/students/', {
                        params: {
                            grade_level: course.level
                        }
                    });
                    totalStudents += studentsResponse.data?.results?.length || 0;
                } catch (error) {
                    console.error(`Error fetching students for course ${course.id}:`, error);
                }
            }

            // Fetch pending results (results not yet approved by this lecturer)
            let pendingResults = 0;
            if (lecturerId) {
                const pendingResponse = await api.get('/results/', {
                    params: {
                        status: 'pending',
                        lecturer: userResponse.data.id
                    }
                });
                pendingResults = pendingResponse.data?.count || pendingResponse.data?.results?.length || 0;
            }

            // Fetch lecturer's announcements
            const announcementsResponse = await api.get('/announcements/', {
                params: {
                    target_audience: 'lecturer'
                }
            });
            const announcements = announcementsResponse.data?.count || announcementsResponse.data?.results?.length || 0;

            // Fetch recent activities
            const activitiesResponse = await api.get('/activity-logs/', {
                params: {
                    user: userResponse.data.id
                }
            });
            const activities = activitiesResponse.data?.results || activitiesResponse.data || [];

            setStats({
                courses: courses.length,
                students: totalStudents,
                pendingResults: pendingResults,
                announcements: announcements
            });
            
            // Get last 5 activities
            setRecentActivities(activities.slice(0, 5));
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            // Keep default values on error
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout userRole="lecturer">
            <div className="lecturer-page">

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
                                    {recentActivities.length === 0 ? (
                                        <tr>
                                            <td colSpan="2">No recent activities</td>
                                        </tr>
                                    ) : (
                                        recentActivities.map(activity => (
                                            <tr key={activity.id}>
                                                <td>{activity.description}</td>
                                                <td>{new Date(activity.created_at).toLocaleDateString()}</td>
                                            </tr>
                                        ))
                                    )}
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