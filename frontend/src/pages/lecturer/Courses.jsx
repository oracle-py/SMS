import { useState, useEffect } from "react";
import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import './Lecturer.css';

export default function Courses() {

    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [students, setStudents] = useState([]);
    const [showStudentsModal, setShowStudentsModal] = useState(false);

    useEffect(() => {
        fetchAssignedCourses();
    }, []);

    const fetchAssignedCourses = async () => {
        setLoading(true);
        try {
            // Get current lecturer's profile
            const userResponse = await api.get('/auth/me/');
            const lecturerId = userResponse.data.profile?.id;
            
            if (lecturerId) {
                // Get lecturer details with assigned courses
                const lecturerResponse = await api.get(`/lecturers/${lecturerId}/`);
                const assignedCourses = lecturerResponse.data.courses || [];
                setCourses(assignedCourses);
            }
        } catch (error) {
            console.error('Error fetching assigned courses:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleViewStudents = async (course) => {
        setSelectedCourse(course);
        setShowStudentsModal(true);
        
        // Fetch students enrolled in this course at the course's level
        try {
            const response = await api.get('/students/', {
                params: {
                    grade_level: course.level
                }
            });
            setStudents(response.data.results || response.data);
        } catch (error) {
            console.error('Error fetching students:', error);
        }
    };

    return (

        <DashboardLayout userRole="lecturer">

            <div className="lecturer-page">

                <div className="lecturer-header">
                    <h1>My Courses</h1>
                </div>

                <div className="lecturer-card">

                    {loading ? (
                        <p>Loading courses...</p>
                    ) : courses.length === 0 ? (
                        <p>No courses assigned to you yet.</p>
                    ) : (
                        <table className="lecturer-table">

                            <thead>

                                <tr>
                                    <th>Code</th>
                                    <th>Course</th>
                                    <th>Level</th>
                                    <th></th>
                                </tr>

                            </thead>

                            <tbody>

                                {courses.map(course => (

                                    <tr key={course.id}>
                                        <td>{course.code}</td>
                                        <td>{course.title}</td>
                                        <td>{course.level}</td>

                                        <td>
                                            <button 
                                                className="lecturer-btn"
                                                onClick={() => handleViewStudents(course)}
                                            >
                                                View Students
                                            </button>
                                        </td>

                                    </tr>

                                ))}

                            </tbody>

                        </table>
                    )}

                </div>

            </div>

            {showStudentsModal && (
                <div className="modal-overlay" onClick={() => setShowStudentsModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Students in {selectedCourse?.title} (Level {selectedCourse?.level})</h2>
                            <button onClick={() => setShowStudentsModal(false)}>×</button>
                        </div>
                        <div className="modal-body">
                            {students.length === 0 ? (
                                <p>No students found for this course.</p>
                            ) : (
                                <table className="lecturer-table">
                                    <thead>
                                        <tr>
                                            <th>Matric Number</th>
                                            <th>Name</th>
                                            <th>Level</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {students.map(student => (
                                            <tr key={student.id}>
                                                <td>{student.student_id}</td>
                                                <td>{student.user?.first_name} {student.user?.last_name}</td>
                                                <td>{student.grade_level}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </div>
                </div>
            )}

        </DashboardLayout>

    );

}