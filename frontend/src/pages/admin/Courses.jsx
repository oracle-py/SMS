import { useState, useEffect } from 'react';
import { HiOutlineMagnifyingGlass, HiOutlinePencil, HiOutlineTrash, HiOutlinePlus } from 'react-icons/hi2';
import DashboardLayout from '../../layouts/DashboardLayout';
import api from '../../api/axios';

function Courses() {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        setLoading(true);
        try {
            const response = await api.get('/courses/');
            setCourses(response.data.results || response.data);
        } catch (error) {
            console.error('Error fetching courses:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredCourses = courses.filter(course =>
        course.course_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.course_title?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <DashboardLayout userRole="admin">
            <div className="ad-page">
                <div className="ad-page-header">
                    <h1>Courses Management</h1>
                    <button className="ad-button-primary">
                        <HiOutlinePlus />
                        Add Course
                    </button>
                </div>

                <div className="ad-search-bar">
                    <HiOutlineMagnifyingGlass />
                    <input
                        type="text"
                        placeholder="Search courses..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                {loading ? (
                    <div className="ad-loading">Loading courses...</div>
                ) : (
                    <div className="ad-table-container">
                        <table className="ad-table">
                            <thead>
                                <tr>
                                    <th>Course Code</th>
                                    <th>Course Title</th>
                                    <th>Credit Units</th>
                                    <th>Level</th>
                                    <th>Semester</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredCourses.length > 0 ? (
                                    filteredCourses.map((course) => (
                                        <tr key={course.id}>
                                            <td>{course.course_code}</td>
                                            <td>{course.course_title}</td>
                                            <td>{course.credit_unit}</td>
                                            <td>{course.level?.name || 'N/A'}</td>
                                            <td>{course.semester?.name_display || course.semester?.name || 'N/A'}</td>
                                            <td>
                                                <span className={`ad-status-badge ${course.is_active ? 'active' : 'inactive'}`}>
                                                    {course.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                            </td>
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
                                        <td colSpan="7" className="ad-empty-state">
                                            No courses found
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

export default Courses;
