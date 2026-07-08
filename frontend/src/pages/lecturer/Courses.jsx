import { useState, useEffect } from "react";
import {
    HiOutlineBookOpen,
    HiOutlineUsers,
    HiOutlineAcademicCap,
    HiOutlineEye,
    HiOutlineXMark,
} from "react-icons/hi2";

import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import "./Lecturer.css";

export default function Courses() {

    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);

    const [selectedCourse, setSelectedCourse] = useState(null);

    const [students, setStudents] = useState([]);

    const [showStudentsModal, setShowStudentsModal] = useState(false);

    const [courseStudentCounts, setCourseStudentCounts] = useState({});

    useEffect(() => {

        fetchAssignedCourses();

    }, []);

    const fetchAssignedCourses = async () => {

        setLoading(true);

        try {

            const userResponse = await api.get("/auth/me/");

            const assignedCourses =
                userResponse.data.data?.profile?.courses || [];

            setCourses(assignedCourses);

            const counts = {};

            for (const course of assignedCourses) {

                try {

                    const response = await api.get("/registrations/", {
                        params: {
                            course: course.id,
                        },
                    });

                    counts[course.id] =
                        response.data?.count ||
                        response.data?.results?.length ||
                        0;

                } catch {

                    counts[course.id] = 0;

                }

            }

            setCourseStudentCounts(counts);

        } catch (error) {

            console.error(error);

        } finally {

            setLoading(false);

        }

    };

    const handleViewStudents = async (course) => {

        setSelectedCourse(course);

        setShowStudentsModal(true);

        try {

            const response = await api.get("/registrations/", {
                params: {
                    course: course.id,
                },
            });

            setStudents(response.data.results || response.data);

        } catch (error) {

            console.error(error);

        }

    };

    const totalStudents =
        Object.values(courseStudentCounts).reduce(
            (total, current) => total + current,
            0
        );

    const totalLevels = [
        ...new Set(
            courses.map(course => course.level?.name || course.level)
        ),
    ].length;

    return (

        <DashboardLayout userRole="lecturer">

            <div className="lecturer-page">

                <div className="courses-hero">

                    <div className="courses-hero-left">

                        <div className="courses-hero-icon">

                            <HiOutlineBookOpen />

                        </div>

                        <div>

                            <h1>My Assigned Courses</h1>

                            <p>

                                View your assigned courses and manage enrolled students.

                            </p>

                        </div>

                    </div>

                    <div className="courses-count">

                        <span>Assigned Courses</span>

                        <h2>{courses.length}</h2>

                    </div>

                </div>

                <div className="courses-stats">

                    <div className="course-stat-card">

                        <div className="course-stat-icon">

                            <HiOutlineAcademicCap />

                        </div>

                        <div>

                            <span>Levels</span>

                            <h2>{totalLevels}</h2>

                        </div>

                    </div>

                </div>

                <div className="lecturer-card">

                    <div className="courses-card-header">

                        <div>

                            <h2>Assigned Courses</h2>

                            <p>

                                Select any course below to view the registered students.

                            </p>

                        </div>

                    </div>

                    {

                        loading ?

                        <div className="courses-loading">

                            <div className="loading-spinner"></div>

                            <p>Loading your assigned courses...</p>

                        </div>

                        :

                        courses.length === 0 ?

                        <div className="courses-empty">

                            <HiOutlineBookOpen className="empty-icon" />

                            <h2>No Courses Assigned</h2>

                            <p>

                                Your administrator has not assigned any course to your account yet.

                            </p>

                        </div>

                        :

                        <div className="table-wrapper">

                            <table className="lecturer-table premium-table">

                                <thead>

                                    <tr>

                                        <th>Course</th>

                                        <th>Academic Level</th>

                                        <th>Enrolled Students</th>

                                        <th style={{width:"170px"}}>

                                            Action

                                        </th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {

                                        courses.map(course => (

                                            <tr key={course.id}>

                                                <td>

                                                    <div className="course-info">

                                                        <div className="course-code">

                                                            {course.course_code}

                                                        </div>

                                                        <div>

                                                            <h4>

                                                                {course.course_title}

                                                            </h4>

                                                        </div>

                                                    </div>

                                                </td>

                                                <td>

                                                    <span className="level-pill">

                                                        {course.level?.name || course.level}

                                                    </span>

                                                </td>

                                                <td>

                                                    <span className="student-pill">

                                                        <HiOutlineUsers />

                                                        {courseStudentCounts[course.id] || 0}

                                                        Students

                                                    </span>

                                                </td>

                                                <td>

                                                    <button

                                                        className="view-students-btn"

                                                        onClick={() => handleViewStudents(course)}

                                                    >

                                                        <HiOutlineEye />

                                                        View Students

                                                    </button>

                                                </td>

                                            </tr>

                                        ))

                                    }

                                </tbody>

                            </table>

                        </div>

                    }

                </div>

            </div>

                {showStudentsModal && (

        <div
            className="modal-overlay"
            onClick={() => setShowStudentsModal(false)}
        >

            <div
                className="students-modal"
                onClick={(e) => e.stopPropagation()}
            >

                <div className="students-modal-header">

                    <div>

                        <span className="modal-badge">

                            {selectedCourse?.course_code}

                        </span>

                        <h2>

                            {selectedCourse?.course_title}

                        </h2>

                        <p>

                            {selectedCourse?.level?.name || selectedCourse?.level}

                            •

                            {students.length} Student{students.length !== 1 ? "s" : ""}

                        </p>

                    </div>

                    <button
                        className="modal-close-btn"
                        onClick={() => setShowStudentsModal(false)}
                    >

                        <HiOutlineXMark />

                    </button>

                </div>

                <div className="students-modal-body">

                    {

                        students.length === 0 ?

                        <div className="courses-empty">

                            <HiOutlineUsers className="empty-icon"/>

                            <h3>

                                No Registered Students

                            </h3>

                            <p>

                                There are currently no students registered for this course.

                            </p>

                        </div>

                        :

                        <table className="lecturer-table premium-table">

                            <thead>

                                <tr>

                                    <th>Student</th>

                                    <th>Matric Number</th>

                                    <th>Academic Level</th>

                                </tr>

                            </thead>

                            <tbody>

                                {

                                    students.map(registration => {

                                        const student = registration.student;

                                        const initials = `${student?.user?.first_name?.[0] || ""}${student?.user?.last_name?.[0] || ""}`;

                                        return (

                                            <tr key={registration.id}>

                                                <td>

                                                    <div className="student-row">

                                                        <div className="student-avatar">

                                                            {initials.toUpperCase()}

                                                        </div>

                                                        <div>

                                                            <h4>

                                                                {student?.user?.first_name}{" "}

                                                                {student?.user?.last_name}

                                                            </h4>

                                                            <span>

                                                                Student

                                                            </span>

                                                        </div>

                                                    </div>

                                                </td>

                                                <td>

                                                    <span className="matric-pill">

                                                        {student?.student_id || "N/A"}

                                                    </span>

                                                </td>

                                                <td>

                                                    <span className="level-pill">

                                                        {student?.grade_level || "N/A"}

                                                    </span>

                                                </td>

                                            </tr>

                                        );

                                    })

                                }

                            </tbody>

                        </table>

                    }

                </div>

            </div>

        </div>

    )}
        </DashboardLayout>
    );
}