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
            
            // Use courses directly from profile data
            const courses = userResponse.data.data?.profile?.courses || [];
            
            // Fetch lecturer's students (total students across all assigned courses)
            let totalStudents = 0;
            for (const course of courses) {
                try {
                    const studentsResponse = await api.get('/registrations/', {
                        params: {
                            course: course.id
                        }
                    });
                    // Handle both paginated and non-paginated responses
                    const count = studentsResponse.data?.count || studentsResponse.data?.results?.length || 0;
                    totalStudents += count;
                } catch (error) {
                    console.error(`Error fetching students for course ${course.id}:`, error);
                }
            }

            // Fetch pending results (results submitted by this lecturer that are pending approval)
            let pendingResults = 0;
            try {
                const pendingResponse = await api.get('/results/', {
                    params: {
                        status: 'pending'
                    }
                });
                // The ResultViewSet automatically filters by lecturer for lecturer users
                pendingResults = pendingResponse.data?.count || pendingResponse.data?.results?.length || 0;
            } catch (error) {
                console.error('Error fetching pending results:', error);
            }

            // Fetch lecturer's announcements
            // The AnnouncementViewSet automatically filters by target_audience for lecturer users
            let announcements = 0;
            try {
                const announcementsResponse = await api.get('/announcements/');
                announcements = announcementsResponse.data?.count || announcementsResponse.data?.results?.length || 0;
            } catch (error) {
                console.error('Error fetching announcements:', error);
            }

            // Fetch recent activities
            // The ActivityLogViewSet automatically filters by user for non-admin users
            let activities = [];
            try {
                const activitiesResponse = await api.get('/activity-logs/');
                activities = activitiesResponse.data?.results || activitiesResponse.data || [];
            } catch (error) {
                console.error('Error fetching activities:', error);
            }

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