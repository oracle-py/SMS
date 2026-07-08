import { useEffect, useState } from "react";
import {
    HiOutlineUserCircle,
    HiOutlineAcademicCap,
    HiOutlineEnvelope
} from "react-icons/hi2";

import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";

import "./student.css";

export default function Lecturers() {

    const [lecturers, setLecturers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchLecturers();
    }, []);

    async function fetchLecturers() {

        setLoading(true);

        try {

            const response = await api.get("/student/lecturers/");

            setLecturers(
                response.data.data ||
                response.data.results ||
                response.data
            );

        }

        catch (error) {

            console.error(error);

        }

        finally {

            setLoading(false);

        }

    }

    const totalCourses = lecturers.reduce(
        (sum, lecturer) => sum + (lecturer.courses?.length || 0),
        0
    );

    const departments = [
        ...new Set(
            lecturers.map(
                lecturer => lecturer.department
            )
        )
    ];

    return (

        <DashboardLayout userRole="student">

            <div className="sc-page">
                <div className="students-header-box">

    <div className="students-header-content">

        <div className="students-header-icon">

            <HiOutlineAcademicCap />

        </div>

        <div className="students-header-text">

            <h1>
                My Lecturers
            </h1>

            <p>
                View all lecturers responsible for your registered courses.
            </p>

        </div>

    </div>

</div>

<div className="ad-stat-strip">

    <div>

        <span>Total Lecturers</span>

        <h2>

            {loading ? "—" : lecturers.length}

        </h2>

    </div>

    <div>

        <span>Registered Courses</span>

        <h2>

            {loading ? "—" : totalCourses}

        </h2>

    </div>

    <div>

        <span>Departments</span>

        <h2>

            {loading ? "—" : departments.length}

        </h2>

    </div>

</div>

<div className="lecturer-card">
    {
    loading ? (

        <div className="ad-loading">

            Loading lecturers...

        </div>

    ) : lecturers.length === 0 ? (

        <div className="ad-empty-state">

            <HiOutlineAcademicCap
                style={{
                    fontSize: "3rem",
                    color: "#94a3b8",
                    marginBottom: "14px"
                }}
            />

            <h3>No Lecturers Found</h3>

            <p>

                You currently do not have any lecturers assigned
                to your registered courses.

            </p>

        </div>

    ) : (

        <table className="lecturer-table">

            <thead>

                <tr>

                    <th>Lecturer</th>

                    <th>Department</th>

                    <th>Courses</th>

                    <th>Email</th>

                    <th>Status</th>

                </tr>

            </thead>

            <tbody>

                {

                    lecturers.map((lecturer) => {

                        const fullName =
                            lecturer.name ||
                            `${lecturer.first_name || ""} ${lecturer.last_name || ""}`;

                        const initials = fullName
                            .trim()
                            .split(" ")
                            .map(name => name[0])
                            .join("")
                            .substring(0, 2)
                            .toUpperCase();

                        return (

                            <tr key={lecturer.id}>

                                <td>

                                    <div className="ad-student">

                                        <div className="ad-avatar">

                                            {

                                                initials ||

                                                <HiOutlineUserCircle />

                                            }

                                        </div>

                                        <div>

                                            <h4>

                                                {fullName}

                                            </h4>

                                            <span>

                                                Lecturer

                                            </span>

                                        </div>

                                    </div>

                                </td>

                                <td>

                                    {lecturer.department || "—"}

                                </td>

                                <td>

                                    <div className="lecturer-course-list">

                                        {

                                            lecturer.courses?.length > 0 ?

                                            lecturer.courses.map(course => (

                                                <div
                                                    key={course.id}
                                                    className="course-pill"
                                                >

                                                    <strong>

                                                        {course.code}

                                                    </strong>

                                                    <span>

                                                        {course.title}

                                                    </span>

                                                </div>

                                            ))

                                            :

                                            <span>

                                                —

                                            </span>

                                        }

                                    </div>

                                </td>

                                <td>

                                    <div className="lecturer-email">

                                        <HiOutlineEnvelope />

                                        <span>

                                            {lecturer.email}

                                        </span>

                                    </div>

                                </td>

                                <td>

                                    <span className="ad-status">

                                        Assigned

                                    </span>

                                </td>

                            </tr>

                        );

                    })

                }

            </tbody>

        </table>

    )
    }
</div>
        </div>
        </DashboardLayout>
    );
}