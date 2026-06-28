import React from "react";
import { useAuth } from "../context/AuthContext";
import DashboardLayout from "../layouts/DashboardLayout";
import "./Parent.css";

function ParentDashboard() {
    const { user } = useAuth();

    // Temporary data until API integration
    const student = {
        name: "John Doe",
        matricNo: "UJ/FNS/20/001",
        department: "Mechanical Engineering",
        level: "400 Level",
        cgpa: "4.21",
        attendance: "92%",
        fees: "Paid",
        semester: "Second Semester",
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

                <div className="parent-header">
                    <h1>Parent Dashboard</h1>
                    <p>
                        Welcome, {user?.first_name || user?.username}
                    </p>
                </div>

                <div className="parent-stats">

                    <div className="parent-card">
                        <h3>Student</h3>
                        <h2>{student.name}</h2>
                    </div>

                    <div className="parent-card">
                        <h3>CGPA</h3>
                        <h2>{student.cgpa}</h2>
                    </div>

                    <div className="parent-card">
                        <h3>Attendance</h3>
                        <h2>{student.attendance}</h2>
                    </div>

                    <div className="parent-card">
                        <h3>School Fees</h3>
                        <h2>{student.fees}</h2>
                    </div>

                </div>

                <div className="parent-grid">

                    <div className="parent-card">

                        <h3>Student Information</h3>

                        <table className="parent-info-table">

                            <tbody>

                                <tr>
                                    <td>Name</td>
                                    <td>{student.name}</td>
                                </tr>

                                <tr>
                                    <td>Matric No.</td>
                                    <td>{student.matricNo}</td>
                                </tr>

                                <tr>
                                    <td>Department</td>
                                    <td>{student.department}</td>
                                </tr>

                                <tr>
                                    <td>Level</td>
                                    <td>{student.level}</td>
                                </tr>

                                <tr>
                                    <td>Semester</td>
                                    <td>{student.semester}</td>
                                </tr>

                            </tbody>

                        </table>

                    </div>

                    <div className="parent-card">

                        <h3>Recent Results</h3>

                        <table className="parent-table">

                            <thead>

                                <tr>
                                    <th>Course</th>
                                    <th>Score</th>
                                    <th>Grade</th>
                                </tr>

                            </thead>

                            <tbody>

                                {student.results.map((course) => (

                                    <tr key={course.course}>

                                        <td>{course.course}</td>

                                        <td>{course.score}</td>

                                        <td>{course.grade}</td>

                                    </tr>

                                ))}

                            </tbody>

                        </table>

                    </div>

                </div>

            </div>

        </DashboardLayout>
    );
}

export default ParentDashboard;