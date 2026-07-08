import { useState, useEffect, useMemo } from "react";
import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import {
    HiOutlineBookOpen,
    HiOutlineSparkles,
    HiOutlineMagnifyingGlass,
    HiOutlineUserCircle,
    HiOutlineClipboardDocumentList,
    HiOutlineAcademicCap
} from "react-icons/hi2";
import "./student.css";

// NOTE on data shape: this assumes /auth/me/ returns the student's registered
// courses at data.data.profile.courses (same place lecturers' assigned courses
// live), where each course may include course_code/code, course_title/title,
// level, units/credit_units, semester, and lecturer { user: { first_name, last_name } }.
// Field names are read defensively with fallbacks since the exact contract
// wasn't provided — adjust the accessor helpers below if your API differs.

function courseCode(course) {
    return course.course_code || course.code || "—";
}

function courseTitle(course) {
    return course.course_title || course.title || "Untitled course";
}

function courseLevel(course) {
    return course.level?.name || course.level || null;
}

function courseUnits(course) {
    return course.units ?? course.credit_units ?? course.credits ?? null;
}

function courseSemester(course) {
    return course.semester?.name || course.semester || null;
}

function lecturerName(course) {
    const lecturer = course.lecturer;
    if (!lecturer) return "Lecturer to be announced";
    const first = lecturer.user?.first_name || lecturer.first_name || "";
    const last = lecturer.user?.last_name || lecturer.last_name || "";
    const full = `${first} ${last}`.trim();
    return full || "Lecturer to be announced";
}

function monogram(course) {
    const code = courseCode(course);
    return code.replace(/[^A-Za-z0-9]/g, "").slice(0, 4) || "CRS";
}

export default function StudentCourses() {

    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [query, setQuery] = useState("");
    const [activeLevel, setActiveLevel] = useState("all");

    useEffect(() => {
        fetchCourses();
    }, []);

    async function fetchCourses() {

        setLoading(true);

        try {

            const response = await api.get("/student/courses/");
            const registered = response.data?.data || response.data?.results || response.data || [];
            setCourses(registered);
        }
        catch (error) {
            console.error("Error fetching courses:", error);
            setCourses([]);
        }
        finally {
            setLoading(false);
        }
    }

    const levels = useMemo(() => {
        const set = new Set();
        courses.forEach(course => {
            const level = courseLevel(course);
            if (level) set.add(String(level));
        });
        return Array.from(set).sort();
    }, [courses]);

    const totalUnits = useMemo(() => {
        return courses.reduce((sum, course) => {
            const units = courseUnits(course);
            return sum + (typeof units === "number" ? units : 0);
        }, 0);
    }, [courses]);

    const filteredCourses = useMemo(() => {

        return courses.filter(course => {

            const matchesLevel =
                activeLevel === "all" || String(courseLevel(course)) === activeLevel;

            if (!matchesLevel) return false;

            if (!query.trim()) return true;

            const haystack = `${courseCode(course)} ${courseTitle(course)} ${lecturerName(course)}`.toLowerCase();
            return haystack.includes(query.trim().toLowerCase());
        });
    }, [courses, query, activeLevel]);

    return (

    <DashboardLayout userRole="student">

        <div className="lecturer-page">

            <div className="students-header-box">

                <div className="students-header-content">

                    <div className="students-header-icon">
                        <HiOutlineBookOpen />
                    </div>

                    <div className="students-header-text">

                        <h1>
                            My Courses
                        </h1>

                        <p>
                            View all courses registered for the current academic session.
                        </p>

                    </div>

                </div>

            </div>

            <div className="ad-stat-strip">

                <div>
                    <span>Registered Courses</span>
                    <h2>
                        {loading ? "—" : courses.length}
                    </h2>
                </div>

                <div>
                    <span>Total Credit Units</span>
                    <h2>
                        {loading ? "—" : totalUnits}
                    </h2>
                </div>

                <div>
                    <span>Academic Levels</span>
                    <h2>
                        {loading ? "—" : levels.length}
                    </h2>
                </div>

            </div>

            <div className="lecturer-card">
                                    {loading ? (

    <div className="ad-loading">

        Loading registered courses...

    </div>

) : courses.length === 0 ? (

    <div className="ad-empty-state">

        <HiOutlineBookOpen
            style={{
                fontSize: "3rem",
                marginBottom: "1rem",
                color: "#6366f1"
            }}
        />

        <h3>No Registered Courses</h3>

        <p>
            You have not registered any courses for this academic session.
        </p>

    </div>

) : (

    <table className="lecturer-table">

        <thead>

            <tr>

                <th>Course Code</th>

                <th>Course Title</th>

                <th>Lecturer</th>

                <th>Level</th>

                <th>Units</th>

                <th>Semester</th>

                <th>Status</th>

            </tr>

        </thead>

        <tbody>

            {courses.map((course) => (

                <tr key={course.id}>

                    <td>

                        <span className="course-code">

                            {courseCode(course)}

                        </span>

                    </td>

                    <td className="course-title">

                        {courseTitle(course)}

                    </td>
                    <td>

                        <div className="ad-student">

                            <div className="ad-avatar">

                                <HiOutlineUserCircle />

                            </div>

                            <div>

                                <h4>

                                    {lecturerName(course)}

                                </h4>

                                <span>

                                    Course Lecturer

                                </span>

                            </div>

                        </div>

                    </td>

                    <td>

                        {courseLevel(course) || "—"}

                    </td>

                    <td>

                        <div className="course-unit">

                            {courseUnits(course) || "—"}

                        </div>

                    </td>

                    <td>

                        <span className="semester-badge">

                            {courseSemester(course) || "N/A"}

                        </span>

                    </td>

                    <td>

                        <span className="ad-status">

                            Registered

                        </span>

                    </td>

                </tr>

            ))}

        </tbody>

    </table>

)}

            </div>

        </div>

    </DashboardLayout>

);

}
