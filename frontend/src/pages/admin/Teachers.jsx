import { useState, useEffect } from 'react';
import { HiOutlineMagnifyingGlass, HiOutlinePencil, HiOutlineTrash, HiOutlinePlus } from 'react-icons/hi2';
import DashboardLayout from '../../layouts/DashboardLayout';
import api from '../../api/axios';

function Teachers() {
    const [teachers, setTeachers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchTeachers();
    }, []);

    const fetchTeachers = async () => {
        setLoading(true);
        try {
            const response = await api.get('/lecturers/');
            setTeachers(response.data.results || response.data);
        } catch (error) {
            console.error('Error fetching lecturers:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredTeachers = teachers.filter(teacher =>
        teacher.user?.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        teacher.user?.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        teacher.staff_id?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <DashboardLayout userRole="admin">
            <div className="ad-page">
                <div className="ad-page-header">
                    <h1>Lecturers Management</h1>
                    <button className="ad-button-primary">
                        <HiOutlinePlus />
                        Add Lecturer
                    </button>
                </div>

                <div className="ad-search-bar">
                    <HiOutlineMagnifyingGlass />
                    <input
                        type="text"
                        placeholder="Search lecturers..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                {loading ? (
                    <div className="ad-loading">Loading lecturers...</div>
                ) : (
                    <div className="ad-table-container">
                        <table className="ad-table">
                            <thead>
                                <tr>
                                    <th>Staff ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Department</th>
                                    <th>Rank</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredTeachers.length > 0 ? (
                                    filteredTeachers.map((teacher) => (
                                        <tr key={teacher.id}>
                                            <td>{teacher.staff_id}</td>
                                            <td>
                                                {teacher.user?.first_name} {teacher.user?.last_name}
                                            </td>
                                            <td>{teacher.user?.email}</td>
                                            <td>{teacher.department_name || 'N/A'}</td>
                                            <td>{teacher.rank}</td>
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
                                            No lecturers found
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

export default Teachers;
