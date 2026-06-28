import { useState, useEffect } from 'react';
import { HiOutlineMagnifyingGlass, HiOutlinePencil, HiOutlineTrash, HiOutlinePlus } from 'react-icons/hi2';
import DashboardLayout from '../../layouts/DashboardLayout';

function Parents() {
    const [parents, setParents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchParents();
    }, []);

    const fetchParents = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/parents/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setParents(data.results || data);
            }
        } catch (error) {
            console.error('Error fetching parents:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredParents = parents.filter(parent =>
        parent.user?.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        parent.user?.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        parent.user?.email?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <DashboardLayout userRole="admin">
            <div className="ad-page">
                <div className="ad-page-header">
                    <h1>Parents Management</h1>
                    <button className="ad-button-primary">
                        <HiOutlinePlus />
                        Add Parent
                    </button>
                </div>

                <div className="ad-search-bar">
                    <HiOutlineMagnifyingGlass />
                    <input
                        type="text"
                        placeholder="Search parents..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                {loading ? (
                    <div className="ad-loading">Loading parents...</div>
                ) : (
                    <div className="ad-table-container">
                        <table className="ad-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                    <th>Occupation</th>
                                    <th>Children</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredParents.length > 0 ? (
                                    filteredParents.map((parent) => (
                                        <tr key={parent.id}>
                                            <td>
                                                {parent.user?.first_name} {parent.user?.last_name}
                                            </td>
                                            <td>{parent.user?.email}</td>
                                            <td>{parent.user?.phone || 'N/A'}</td>
                                            <td>{parent.occupation || 'N/A'}</td>
                                            <td>{parent.children_count || 0}</td>
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
                                            No parents found
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

export default Parents;
