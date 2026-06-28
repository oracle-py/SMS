import { useState, useEffect } from 'react';
import { HiOutlineMagnifyingGlass, HiOutlinePencil, HiOutlineTrash, HiOutlinePlus } from 'react-icons/hi2';
import DashboardLayout from '../../layouts/DashboardLayout';

function Students() {
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchStudents();
    }, []);

    const fetchStudents = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/students/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setStudents(data.results || data);
            }
        } catch (error) {
            console.error('Error fetching students:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredStudents = students.filter(student =>
        student.user?.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.user?.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.student_id?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <DashboardLayout userRole="admin">
            <div className="ad-page">
                <div className="ad-page-header">
                    <h1>Students Management</h1>
                    <button className="ad-button-primary">
                        <HiOutlinePlus />
                        Add Student
                    </button>
                </div>

                <div className="ad-search-bar">
                    <HiOutlineMagnifyingGlass />
                    <input
                        type="text"
                        placeholder="Search students..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                {loading ? (
                    <div className="ad-loading">Loading students...</div>
                ) : (
                    <div className="ad-table-container">
                        <table className="ad-table">
                            <thead>
                                <tr>
                                    <th>Student ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Programme</th>
                                    <th>Grade Level</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredStudents.length > 0 ? (
                                    filteredStudents.map((student) => (
                                        <tr key={student.id}>
                                            <td>{student.student_id || 'N/A'}</td>
                                            <td>
                                                {student.user?.first_name} {student.user?.last_name}
                                            </td>
                                            <td>{student.user?.email}</td>
                                            <td>{student.programme_name || 'N/A'}</td>
                                            <td>{student.grade_level}00 Level</td>
                                            <td>
                                                <div className="ad-action-buttons">
                                                    <button className="ad-button-icon" title="Edit">
                                                        <HiOutlinePencil />
                                                    </button>
                                                    <button className="ad-button-icon" title="Delete">
                                                        <HiOutlineTrash />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="6" className="ad-empty-state">
                                            No students found
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}

export default Students;
