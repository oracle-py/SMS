import { useState, useEffect } from "react";
import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import './Lecturer.css';

export default function Results() {

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
                        
                        // Get existing results for this course
                        const resultsResponse = await api.get('/results/', {
                            params: {
                                course: course.id,
                                lecturer: userResponse.data.id
                            }
                        });
                        const existingResults = resultsResponse.data.results || resultsResponse.data;
                        
                        // Map existing results to student IDs
                        const resultsMap = {};
                        existingResults.forEach(result => {
                            resultsMap[result.student_id] = {
                                ca: result.ca_score,
                                exam: result.exam_score,
                                status: result.status
                            };
                        });
                        
                        return {
                            ...course,
                            students: students,
                            existingResults: resultsMap
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
            const existingResult = course.existingResults[student.id];
            
            // Only include if there's new data or existing data
            if (resultData || existingResult) {
                courseResults.push({
                    student_id: student.id,
                    course_id: course.id,
                    lecturer_id: lecturerId,
                    ca_score: resultData?.ca || existingResult?.ca || 0,
                    exam_score: resultData?.exam || existingResult?.exam || 0
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
            // Refresh data
            fetchCoursesWithStudents();
        } catch (error) {
            console.error('Error saving results:', error);
            alert('Failed to save results');
        }
    };

    return (

        <DashboardLayout userRole="lecturer">

            <div className="lecturer-page">

                <div className="lecturer-header">
                    <h1>Results</h1>
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
                                    <h3>{course.code} - {course.title} (Level {course.level}) - {course.students.length} Students</h3>
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
                                            <th>Total</th>
                                            <th>Grade</th>
                                            <th>Status</th>
                                        </tr>

                                    </thead>

                                    <tbody>

                                        {course.students.map(student => {
                                            const key = `${course.id}-${student.id}`;
                                            const resultData = results[key] || {};
                                            const existingResult = course.existingResults[student.id] || {};
                                            const ca = resultData.ca !== undefined ? resultData.ca : existingResult.ca;
                                            const exam = resultData.exam !== undefined ? resultData.exam : existingResult.exam;
                                            const total = (parseFloat(ca) || 0) + (parseFloat(exam) || 0);
                                            
                                            // Calculate grade
                                            let grade = '-';
                                            if (total >= 70) grade = 'A';
                                            else if (total >= 60) grade = 'B';
                                            else if (total >= 50) grade = 'C';
                                            else if (total >= 45) grade = 'D';
                                            else if (total >= 40) grade = 'E';
                                            else if (total > 0) grade = 'F';
                                            
                                            const status = existingResult.status || '-';
                                            
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
                                                            value={resultData.ca !== undefined ? resultData.ca : (existingResult.ca || '')}
                                                            onChange={(e) => handleScoreChange(course.id, student.id, 'ca', e.target.value)}
                                                            disabled={status === 'approved'}
                                                        />
                                                    </td>
                                                    <td>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            max="60"
                                                            className="score-input"
                                                            placeholder="Exam"
                                                            value={resultData.exam !== undefined ? resultData.exam : (existingResult.exam || '')}
                                                            onChange={(e) => handleScoreChange(course.id, student.id, 'exam', e.target.value)}
                                                            disabled={status === 'approved'}
                                                        />
                                                    </td>
                                                    <td>{total > 0 ? total.toFixed(2) : '-'}</td>
                                                    <td>{grade}</td>
                                                    <td>
                                                        <span className={`status-badge status-${status}`}>
                                                            {status.charAt(0).toUpperCase() + status.slice(1)}
                                                        </span>
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