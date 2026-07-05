import { useState, useEffect } from "react";
import {
    HiOutlineTrash,
    HiOutlinePlus,
    HiOutlineBookOpen
} from "react-icons/hi2";

import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import { useDashboardRefresh } from "../../context/DashboardContext";
import CreateCourseDrawer from "./components/CreateCourseDrawer";

import "./admin.css";

function Courses() {

    const { refreshDashboard } = useDashboardRefresh();

    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [drawerOpen, setDrawerOpen] = useState(false);

    useEffect(() => {
        fetchCourses();
    }, []);

    async function fetchCourses() {
        setLoading(true);

        try {
            const response = await api.get("/courses/");
            setCourses(response.data.results || response.data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    const handleDrawerClose = () => {
        setDrawerOpen(false);
        fetchCourses();
        refreshDashboard();
    };

    const handleDelete = async (courseId) => {
        if (!window.confirm('Are you sure you want to delete this course?')) {
            return;
        }
        try {
            await api.delete(`/courses/${courseId}/`);
            fetchCourses();
            refreshDashboard();
        } catch (error) {
            console.error('Error deleting course:', error);
            alert('Failed to delete course');
        }
    };


    return (
        <DashboardLayout>

            <div className="ad-page">

                <div className="students-header-box">

                    <div className="students-header-content">

                        <div className="students-header-icon">

                            <HiOutlineBookOpen />

                        </div>

                        <div className="students-header-text">

                            <h1>
                                Courses
                            </h1>

                            <p>
                                Manage all registered courses across the institution.
                            </p>

                        </div>

                    </div>

                    <button className="ad-button-primary" onClick={() => setDrawerOpen(true)}>

                        <HiOutlinePlus />

                        Add Course

                    </button>

                </div>

                <div className="ad-stat-strip">

                    <div>

                        <span>Total Courses</span>

                        <h2>{courses.length}</h2>

                    </div>

                </div>

                {
                    loading ?

                        <div className="ad-loading">
                            Loading courses...
                        </div>

                        :

                        <div className="ad-card">

                            <table className="ad-table">

                                <thead>

                                    <tr>

                                        <th>Course</th>
                                        <th>Code</th>
                                        <th>Units</th>
                                        <th>Level</th>
                                        <th>Semester</th>
                                        <th>Status</th>
                                        <th></th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {

                                        courses.length > 0 ?

                                            courses.map((course) => {

                                                const initials = course.course_code
                                                    ?.substring(0, 2)
                                                    .toUpperCase();

                                                return (

                                                    <tr key={course.id}>

                                                        <td>

                                                            <div className="ad-student">

                                                                <div className="ad-avatar">

                                                                    {initials}

                                                                </div>

                                                                <div>

                                                                    <h4>

                                                                        {course.course_title}

                                                                    </h4>

                                                                    <span>

                                                                        {course.course_code}

                                                                    </span>

                                                                </div>

                                                            </div>

                                                        </td>

                                                        <td>

                                                            {course.course_code}

                                                        </td>

                                                        <td>

                                                            {course.credit_unit}

                                                        </td>

                                                        <td>

                                                            {course.level?.name || "—"}

                                                        </td>

                                                        <td>

                                                            {course.semester?.name_display ||
                                                                course.semester?.name ||
                                                                "—"}

                                                        </td>

                                                        <td>

                                                            <span className="ad-status">

                                                                {course.is_active ? "Active" : "Inactive"}

                                                            </span>

                                                        </td>

                                                        <td>

                                                            <div className="ad-action-buttons">

                                                                <button onClick={() => handleDelete(course.id)}>

                                                                    <HiOutlineTrash />

                                                                </button>

                                                            </div>

                                                        </td>

                                                    </tr>

                                                );

                                            })

                                            :

                                            <tr>

                                                <td
                                                    colSpan="7"
                                                    className="ad-empty-state"
                                                >

                                                    No courses found.

                                                </td>

                                            </tr>

                                    }

                                </tbody>

                            </table>

                        </div>

                }

                <CreateCourseDrawer 
                    open={drawerOpen}
                    onClose={handleDrawerClose}
                />

            </div>

        </DashboardLayout>
    );
}

export default Courses;