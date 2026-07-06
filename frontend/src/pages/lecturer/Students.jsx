import { useState, useEffect } from "react";
import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import './Lecturer.css';

export default function Students() {

    const [coursesWithStudents, setCoursesWithStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [results, setResults] = useState({});

    useEffect(() => {
        fetchCoursesWithStudents();
    }, []);

    const fetchCoursesWithStudents = async () => {
        setLoading(true);
        try {
            // Get current lecturer's profile
            const userResponse = await api.get('/auth/me/');
            const lecturerId = userResponse.data.profile?.id;
            
            if (lecturerId) {
                // Get lecturer details with assigned courses
                const lecturerResponse = await api.get(`/lecturers/${lecturerId}/`);
                const assignedCourses = lecturerResponse.data.courses || [];
                
                // For each course, get students at that level
                const coursesData = await Promise.all(
                    assignedCourses.map(async (course) => {
                        const studentsResponse = await api.get('/students/', {
                            params: {
                                grade_level: course.level
                            }
                        });
                        const students = studentsResponse.data.results || studentsResponse.data;
                        
                        return {
                            ...course,
                            students: students
                        };
                    })
                );
                
                setCoursesWithStudents(coursesData);
            }
        } catch (error) {
            console.error('Error fetching courses with students:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleScoreChange = (courseId, studentId, field, value) => {
        const key = `${courseId}-${studentId}`;
        setResults(prev => ({
            ...prev,
            [key]: {
                ...prev[key],
                [field]: value
            }
        }));
    };

    const handleSaveResults = async (course) => {
        const courseResults = [];
        
        // Get current user ID (lecturer)
        const userResponse = await api.get('/auth/me/');
        const lecturerId = userResponse.data.id;
        
        course.students.forEach(student => {
            const key = `${course.id}-${student.id}`;
            const resultData = results[key];
            if (resultData) {
                courseResults.push({
                    student_id: student.id,
                    course_id: course.id,
                    lecturer_id: lecturerId,
                    ca_score: resultData.ca || 0,
                    exam_score: resultData.exam || 0
                });
            }
        });

        if (courseResults.length === 0) {
            alert('Please enter scores for at least one student');
            return;
        }

        try {
            await api.post('/results/batch/', {
                results: courseResults
            });
            alert('Results submitted for approval');
            // Clear results for this course
            const updatedResults = { ...results };
            course.students.forEach(student => {
                const key = `${course.id}-${student.id}`;
                delete updatedResults[key];
            });
            setResults(updatedResults);
        } catch (error) {
            console.error('Error saving results:', error);
            alert('Failed to save results');
        }
    };

    return (

        <DashboardLayout userRole="lecturer">

            <div className="lecturer-page">

                <div className="lecturer-header">
                    <h1>Students by Course</h1>
                </div>

                <div className="lecturer-card">

                    {loading ? (
                        <p>Loading courses and students...</p>
                    ) : coursesWithStudents.length === 0 ? (
                        <p>No courses assigned to you yet.</p>
                    ) : (
                        coursesWithStudents.map(course => (
                            <div key={course.id} className="course-section">
                                <div className="course-header">
                                    <h3>{course.code} - {course.title} (Level {course.level})</h3>
                                    <button 
                                        className="lecturer-btn"
                                        onClick={() => handleSaveResults(course)}
                                    >
                                        Save Results
                                    </button>
                                </div>

                                <table className="lecturer-table">

                                    <thead>

                                        <tr>
                                            <th>Student Name</th>
                                            <th>Matric Number</th>
                                            <th>CA Score</th>
                                            <th>Exam Score</th>
                                        </tr>

                                    </thead>

                                    <tbody>

                                        {course.students.map(student => {
                                            const key = `${course.id}-${student.id}`;
                                            const resultData = results[key] || { ca: '', exam: '' };
                                            
                                            return (
                                                <tr key={student.id}>
                                                    <td>{student.user?.first_name} {student.user?.last_name}</td>
                                                    <td>{student.student_id}</td>
                                                    <td>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            max="40"
                                                            className="score-input"
                                                            placeholder="CA"
                                                            value={resultData.ca}
                                                            onChange={(e) => handleScoreChange(course.id, student.id, 'ca', e.target.value)}
                                                        />
                                                    </td>
                                                    <td>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            max="60"
                                                            className="score-input"
                                                            placeholder="Exam"
                                                            value={resultData.exam}
                                                            onChange={(e) => handleScoreChange(course.id, student.id, 'exam', e.target.value)}
                                                        />
                                                    </td>
                                                </tr>
                                            );
                                        })}

                                    </tbody>

                                </table>
                            </div>
                        ))
                    )}

                </div>

            </div>

        </DashboardLayout>

    );

}