import { useState, useEffect } from "react";
import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import {
    HiOutlineAcademicCap,
    HiOutlineCalendarDays,
    HiOutlineCheckCircle,
    HiOutlineUsers,
    HiOutlineChevronDown
} from "react-icons/hi2";
import "./Lecturer.css";

function getToday() {
    return new Date().toISOString().split("T")[0];
}

function formatDate(dateStr) {
    if (!dateStr) return "";
    return new Date(`${dateStr}T00:00:00`).toLocaleDateString(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric"
    });
}

function initialsOf(student) {
    const first = student.user?.first_name?.charAt(0) || "";
    const last = student.user?.last_name?.charAt(0) || "";
    return `${first}${last}`.toUpperCase() || "?";
}

export default function Students() {

    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);

    const [expandedIds, setExpandedIds] = useState(new Set());
    const [attendanceDates, setAttendanceDates] = useState({});
    const [attendance, setAttendance] = useState({});
    const [publishingId, setPublishingId] = useState(null);
    const [publishedMap, setPublishedMap] = useState({});

    useEffect(() => {
        fetchCourses();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    async function fetchCourses() {

        setLoading(true);

        try {

            const userResponse = await api.get("/auth/me/");
            
            if (!userResponse.data?.data?.profile) {
                console.error("No profile data found in response");
                setCourses([]);
                return;
            }
            
            const assignedCourses = userResponse.data.data.profile.courses || [];
            const today = getToday();

            // Reset attendance state for today
            const newAttendanceState = {};
            const newPublishedMap = {};

            const populatedCourses = await Promise.all(
                assignedCourses.map(async course => {

                    try {
                        const response = await api.get("/registrations/", {
                            params: { 
                                course: course.id,
                                session: course.session_id,
                                semester: course.semester_id
                            }
                        });

                        const registrations = response.data.results || response.data || [];
                        const students = registrations.map(reg => reg.student).filter(Boolean);
                        
                        // Fetch existing attendance for today for this course
                        try {
                            const attendanceResponse = await api.get("/attendance/", {
                                params: { 
                                    course: course.id,
                                    date: today
                                }
                            });
                            const attendanceRecords = attendanceResponse.data.results || attendanceResponse.data || [];
                            
                            // Check if attendance is published for this course today
                            if (attendanceRecords.length > 0) {
                                newPublishedMap[course.id] = today;
                            }
                            
                            // Load existing attendance into state
                            attendanceRecords.forEach(record => {
                                const key = `${course.id}-${today}-${record.student}`;
                                newAttendanceState[key] = record.status;
                            });
                        } catch (attError) {
                            console.error(`Error fetching attendance for course ${course.id}:`, attError);
                        }

                        return { ...course, students };
                    } catch (courseError) {
                        console.error(`Error fetching students for course ${course.id}:`, courseError);
                        return { ...course, students: [] };
                    }
                })
            );

            // Set the new attendance state
            setAttendance(newAttendanceState);
            setPublishedMap(newPublishedMap);
            setCourses(populatedCourses);
        }
        catch (error) {
            console.error("Error fetching courses:", error);
            setCourses([]);
        }
        finally {
            setLoading(false);
        }
    }

    function toggleExpand(courseId) {
        setExpandedIds(prev => {
            const next = new Set(prev);
            if (next.has(courseId)) {
                next.delete(courseId);
            } else {
                next.add(courseId);
            }
            return next;
        });
    }

    function getCourseDate(courseId) {
        return attendanceDates[courseId] || getToday();
    }

    function handleDateChange(courseId, date) {
        setAttendanceDates(prev => ({ ...prev, [courseId]: date }));
        
        // When date changes, we should reload attendance for the new date
        const newDate = date;
        const course = courses.find(c => c.id === courseId);
        if (course) {
            loadAttendanceForDate(course, newDate);
        }
    }
    
    async function loadAttendanceForDate(course, date) {
        try {
            const attendanceResponse = await api.get("/attendance/", {
                params: { 
                    course: course.id,
                    date: date
                }
            });
            const attendanceRecords = attendanceResponse.data.results || attendanceResponse.data || [];
            
            // Clear old attendance keys for this course and load new ones
            const newAttendanceState = { ...attendance };
            
            // Remove all keys for this course (for any date)
            Object.keys(newAttendanceState).forEach(key => {
                if (key.startsWith(`${course.id}-`)) {
                    delete newAttendanceState[key];
                }
            });
            
            // Load attendance for the new date
            attendanceRecords.forEach(record => {
                const key = `${course.id}-${date}-${record.student}`;
                newAttendanceState[key] = record.status;
            });
            
            setAttendance(newAttendanceState);
            
            // Update published map
            if (attendanceRecords.length > 0) {
                setPublishedMap(prev => ({ ...prev, [course.id]: date }));
            } else {
                setPublishedMap(prev => {
                    const next = { ...prev };
                    delete next[course.id];
                    return next;
                });
            }
        } catch (attError) {
            console.error(`Error fetching attendance for course ${course.id} on ${date}:`, attError);
        }
    }

    function getStatus(courseId, studentId) {
        const key = `${courseId}-${getCourseDate(courseId)}-${studentId}`;
        return attendance[key]; // Returns undefined if not set (unmarked state)
    }

    function setStatus(courseId, studentId, status) {
        const key = `${courseId}-${getCourseDate(courseId)}-${studentId}`;
        setAttendance(prev => ({ ...prev, [key]: status }));
    }

    function getMarkedSummary(course) {
        const date = getCourseDate(course.id);
        let present = 0;
        let absent = 0;
        let marked = 0;

        course.students.forEach(student => {
            const key = `${course.id}-${date}-${student.id}`;
            const status = attendance[key];
            if (status === "absent") {
                absent += 1;
                marked += 1;
            } else if (status === "present") {
                present += 1;
                marked += 1;
            }
        });

        return { present, absent, marked, total: course.students.length };
    }
    
    function isAttendancePublished(course) {
        const date = getCourseDate(course.id);
        return publishedMap[course.id] === date;
    }

    async function handlePublishAttendance(course) {

        const date = getCourseDate(course.id);

        // Validate that all students have been marked
        const allMarked = course.students.every(student => {
            const status = getStatus(course.id, student.id);
            return status === "present" || status === "absent";
        });

        if (!allMarked) {
            alert("Please mark attendance for all students before publishing.");
            return;
        }

        const payload = {
            date,
            course_id: course.id,
            attendance: course.students.map(student => ({
                student_id: student.id,
                present: getStatus(course.id, student.id) === "present"
            }))
        };

        setPublishingId(course.id);

        try {

            console.log(payload);

            const response = await api.post("/attendance/batch/", payload);
            
            if (response.data) {
                setPublishedMap(prev => ({ ...prev, [course.id]: date }));
                alert("Attendance published successfully!");
            }
        }
        catch (error) {
            console.error(error);
            alert("Unable to publish attendance. Please try again.");
        }
        finally {
            setPublishingId(null);
        }
    }

    const totalStudents = new Set();
    courses.forEach(course => {
        course.students.forEach(student => {
            totalStudents.add(student.id);
        });
    });
    const uniqueStudentCount = totalStudents.size;

    return (
        <DashboardLayout userRole="lecturer">

            <div className="att-page">

                <div className="att-page-header">
                    <div>
                        <h1>Student Attendance</h1>
                        <p>Pick a course, choose a date, and mark who was in class.</p>
                    </div>

                    {!loading && courses.length > 0 && (
                        <div className="att-summary-pill">
                            <HiOutlineUsers />
                            {uniqueStudentCount} students · {courses.length} course{courses.length === 1 ? "" : "s"}
                        </div>
                    )}
                </div>

                {loading ? (

                    <div className="att-state-card">
                        <div className="att-spinner" />
                        <p>Loading your courses…</p>
                    </div>

                ) : courses.length === 0 ? (

                    <div className="att-state-card">
                        <HiOutlineAcademicCap className="att-empty-icon" />
                        <h3>No courses assigned</h3>
                        <p>You currently have no assigned courses.</p>
                    </div>

                ) : (

                    <div className="att-card-list">

                        {courses.map(course => {

                            const isOpen = expandedIds.has(course.id);
                            const date = getCourseDate(course.id);
                            const summary = getMarkedSummary(course);
                            const isPublished = publishedMap[course.id] === date;
                            const isPublishing = publishingId === course.id;
                            
                            // Check if all students have been marked
                            const allMarked = course.students.every(student => {
                                const status = getStatus(course.id, student.id);
                                return status === "present" || status === "absent";
                            });

                            return (
                                <div
                                    key={course.id}
                                    className={`att-card ${isOpen ? "is-open" : ""}`}
                                >

                                    <button
                                        type="button"
                                        className="att-card-header"
                                        onClick={() => toggleExpand(course.id)}
                                        aria-expanded={isOpen}
                                    >

                                        <div className="att-card-title">

                                            <span className="att-course-code">
                                                {course.course_code || course.code}
                                            </span>

                                            <div className="att-card-title-text">
                                                <h2>{course.course_title || course.title}</h2>
                                                <p>
                                                    Level {course.level?.name || course.level} ·{" "}
                                                    {course.students.length} student
                                                    {course.students.length === 1 ? "" : "s"}
                                                </p>
                                            </div>

                                        </div>

                                        <div className="att-card-header-right">

                                            {summary.total > 0 && (
                                                <span
                                                    className={
                                                        "att-status-pill" +
                                                        (summary.marked === 0
                                                            ? " unmarked"
                                                            : "")
                                                    }
                                                >
                                                    {summary.marked === 0
                                                        ? "Not marked yet"
                                                        : `${summary.marked}/${summary.total} marked`}
                                                </span>
                                            )}

                                            <HiOutlineChevronDown className="att-chevron" />

                                        </div>

                                    </button>

                                    <div className="att-card-body-wrapper">
                                        <div className="att-card-body">

                                            <div className="att-toolbar">

                                                <label className="att-date-field">
                                                    <span>
                                                        <HiOutlineCalendarDays />
                                                        Attendance date
                                                    </span>
                                                    <input
                                                        type="date"
                                                        value={date}
                                                        onChange={(e) =>
                                                            handleDateChange(course.id, e.target.value)
                                                        }
                                                    />
                                                </label>

                                                <button
                                                    type="button"
                                                    className="att-publish-btn"
                                                    onClick={() => handlePublishAttendance(course)}
                                                    disabled={isPublishing || course.students.length === 0 || !allMarked}
                                                >
                                                    {isPublishing
                                                        ? "Publishing…"
                                                        : isPublished
                                                        ? "Republish attendance"
                                                        : "Publish attendance"}
                                                </button>

                                            </div>

                                            {isPublished && (
                                                <div className="att-published-note">
                                                    <HiOutlineCheckCircle />
                                                    Published for {formatDate(date)} — visible to students now.
                                                </div>
                                            )}

                                            {course.students.length === 0 ? (

                                                <div className="att-empty-row">
                                                    No students registered for this course.
                                                </div>

                                            ) : (

                                                <div className="att-single-list">

                                                    <h3>Mark attendance — {formatDate(date)}</h3>

                                                    <ul>
                                                        {course.students.map(student => {

                                                            const status = getStatus(course.id, student.id);

                                                            return (
                                                                <li key={student.id}>
                                                                    <div className="att-student-info">
                                                                        <div className="att-avatar">
                                                                            {initialsOf(student)}
                                                                        </div>
                                                                        <div className="att-roster-text">
                                                                            <strong>
                                                                                {student.user?.first_name}{" "}
                                                                                {student.user?.last_name}
                                                                            </strong>
                                                                            <span>
                                                                                {student.student_id || student.id}
                                                                            </span>
                                                                        </div>
                                                                    </div>

                                                                    <div className="att-toggle">

                                                                        <button
                                                                            type="button"
                                                                            className={
                                                                                status === "present"
                                                                                    ? "att-status-btn present active"
                                                                                    : "att-status-btn present"
                                                                            }
                                                                            onClick={() =>
                                                                                setStatus(
                                                                                    course.id,
                                                                                    student.id,
                                                                                    "present"
                                                                                )
                                                                            }
                                                                        >
                                                                            Present
                                                                        </button>

                                                                        <button
                                                                            type="button"
                                                                            className={
                                                                                status === "absent"
                                                                                    ? "att-status-btn absent active"
                                                                                    : "att-status-btn absent"
                                                                            }
                                                                            onClick={() =>
                                                                                setStatus(
                                                                                    course.id,
                                                                                    student.id,
                                                                                    "absent"
                                                                                )
                                                                            }
                                                                        >
                                                                            Absent
                                                                        </button>

                                                                    </div>

                                                                </li>
                                                            );
                                                        })}
                                                    </ul>

                                                </div>

                                            )}

                                        </div>
                                    </div>

                                </div>
                            );
                        })}

                    </div>

                )}

            </div>

        </DashboardLayout>
    );
}
