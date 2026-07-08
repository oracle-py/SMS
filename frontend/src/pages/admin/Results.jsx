import React, { useState, useEffect } from "react";
import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import {
    HiOutlineClipboardDocumentList,
    HiOutlineAcademicCap,
    HiOutlineUser,
    HiOutlineCheckCircle,
    HiOutlineXCircle,
    HiOutlineXMark,
    HiOutlineClock,
    HiOutlineAdjustmentsHorizontal,
    HiOutlineMagnifyingGlass
} from "react-icons/hi2";
import "./admin.css";

export default function Results() {
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('pending'); // pending, approved, rejected, all
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedResult, setSelectedResult] = useState(null);
    const [rejectReason, setRejectReason] = useState('');
    const [showRejectModal, setShowRejectModal] = useState(false);

    useEffect(() => {
        fetchResults();
    }, [filter]);

    const fetchResults = async () => {
        setLoading(true);
        try {
            const params = {};
            if (filter !== 'all') {
                params.status = filter;
            }
            
            const response = await api.get('/results/', { params });
            setResults(response.data.results || response.data || []);
        } catch (error) {
            console.error('Error fetching results:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (resultId) => {
        try {
            await api.post(`/results/${resultId}/approve/`);
            fetchResults();
        } catch (error) {
            console.error('Error approving result:', error);
            alert('Failed to approve result. Please try again.');
        }
    };

    const handleReject = async () => {
        if (!selectedResult || !rejectReason.trim()) {
            alert('Please provide a reason for rejection.');
            return;
        }

        try {
            await api.post(`/results/${selectedResult.id}/reject/`, {
                remarks: rejectReason
            });
            setShowRejectModal(false);
            setSelectedResult(null);
            setRejectReason('');
            fetchResults();
        } catch (error) {
            console.error('Error rejecting result:', error);
            alert('Failed to reject result. Please try again.');
        }
    };

    const openRejectModal = (result) => {
        setSelectedResult(result);
        setRejectReason('');
        setShowRejectModal(true);
    };

    const closeRejectModal = () => {
        setShowRejectModal(false);
        setSelectedResult(null);
        setRejectReason('');
    };

    const filteredResults = results.filter(result => {
        if (!searchTerm) return true;
        const searchLower = searchTerm.toLowerCase();
        return (
            result.student?.username?.toLowerCase().includes(searchLower) ||
            result.student?.first_name?.toLowerCase().includes(searchLower) ||
            result.student?.last_name?.toLowerCase().includes(searchLower) ||
            result.course?.course_code?.toLowerCase().includes(searchLower) ||
            result.course?.course_title?.toLowerCase().includes(searchLower)
        );
    });

    const getStatusBadge = (status) => {
        const statusConfig = {
            pending: { color: 'orange', icon: HiOutlineClock, text: 'Pending' },
            approved: { color: 'green', icon: HiOutlineCheckCircle, text: 'Published' },
            rejected: { color: 'red', icon: HiOutlineXCircle, text: 'Rejected' }
        };
        const config = statusConfig[status] || statusConfig.pending;
        const Icon = config.icon;
        
        return (
            <span className={`status-badge status-${config.color}`}>
                <Icon />
                {config.text}
            </span>
        );
    };

    return (
        <DashboardLayout userRole="admin">
            <div className="ad-page">
                <div className="ad-page-header">
                    <div>
                        <h1>Results Management</h1>
                        <p>Review and manage student results submitted by lecturers</p>
                    </div>
                </div>

                <div className="ad-filters">
                    <div className="ad-search-box">
                        <HiOutlineMagnifyingGlass />
                        <input
                            type="text"
                            placeholder="Search by student, course..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <div className="ad-filter-buttons">
                        <button
                            className={`ad-filter-btn ${filter === 'pending' ? 'active' : ''}`}
                            onClick={() => setFilter('pending')}
                        >
                            <HiOutlineClock />
                            Pending
                        </button>
                        <button
                            className={`ad-filter-btn ${filter === 'approved' ? 'active' : ''}`}
                            onClick={() => setFilter('approved')}
                        >
                            <HiOutlineCheckCircle />
                            Published
                        </button>
                        <button
                            className={`ad-filter-btn ${filter === 'rejected' ? 'active' : ''}`}
                            onClick={() => setFilter('rejected')}
                        >
                            <HiOutlineXCircle />
                            Rejected
                        </button>
                        <button
                            className={`ad-filter-btn ${filter === 'all' ? 'active' : ''}`}
                            onClick={() => setFilter('all')}
                        >
                            <HiOutlineAdjustmentsHorizontal />
                            All
                        </button>
                    </div>
                </div>

                {loading ? (
                    <div className="ad-loading">
                        <div className="ad-spinner"></div>
                        <p>Loading results...</p>
                    </div>
                ) : filteredResults.length === 0 ? (
                    <div className="ad-empty-state">
                        <HiOutlineClipboardDocumentList className="empty-icon" />
                        <h3>No results found</h3>
                        <p>
                            {filter === 'pending' 
                                ? 'No pending results to review' 
                                : `No ${filter} results found`}
                        </p>
                    </div>
                ) : (
                    <div className="ad-table-container">
                        <table className="ad-table">
                            <thead>
                                <tr>
                                    <th>Student</th>
                                    <th>Course</th>
                                    <th>Lecturer</th>
                                    <th>CA Score</th>
                                    <th>Exam Score</th>
                                    <th>Total</th>
                                    <th>Grade</th>
                                    <th>Status</th>
                                    <th>Submitted</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredResults.map((result) => (
                                    <tr key={result.id}>
                                        <td>
                                            <div className="ad-user-cell">
                                                <div className="ad-user-avatar">
                                                    {result.student?.first_name?.[0] || '?'}
                                                    {result.student?.last_name?.[0] || ''}
                                                </div>
                                                <div>
                                                    <div className="ad-user-name">
                                                        {result.student?.first_name} {result.student?.last_name}
                                                    </div>
                                                    <div className="ad-user-email">
                                                        {result.student?.username}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <div>
                                                <div className="ad-course-code">
                                                    {result.course?.course_code || 'N/A'}
                                                </div>
                                                <div className="ad-course-title">
                                                    {result.course?.course_title || 'N/A'}
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            {result.lecturer?.first_name} {result.lecturer?.last_name}
                                        </td>
                                        <td>{result.ca_score || 0}</td>
                                        <td>{result.exam_score || 0}</td>
                                        <td className="ad-total-score">
                                            {result.total_score || 0}
                                        </td>
                                        <td className="ad-grade">
                                            {result.grade || 'N/A'}
                                        </td>
                                        <td>{getStatusBadge(result.status)}</td>
                                        <td>
                                            {result.submitted_at 
                                                ? new Date(result.submitted_at).toLocaleDateString()
                                                : 'N/A'}
                                        </td>
                                        <td>
                                            {result.status === 'pending' && (
                                                <div className="ad-action-buttons">
                                                    <button
                                                        className="ad-btn ad-btn-approve"
                                                        onClick={() => handleApprove(result.id)}
                                                        title="Approve and publish"
                                                    >
                                                        <HiOutlineCheckCircle />
                                                    </button>
                                                    <button
                                                        className="ad-btn ad-btn-reject"
                                                        onClick={() => openRejectModal(result)}
                                                        title="Reject and return to lecturer"
                                                    >
                                                        <HiOutlineXCircle />
                                                    </button>
                                                </div>
                                            )}
                                            {result.status === 'rejected' && result.remarks && (
                                                <div className="ad-reject-reason" title={result.remarks}>
                                                    {result.remarks.substring(0, 30)}...
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Reject Modal */}
                {showRejectModal && (
                    <div className="ad-modal-overlay" onClick={closeRejectModal}>
                        <div className="ad-modal" onClick={(e) => e.stopPropagation()}>
                            <div className="ad-modal-header">
                                <h3>Reject Result</h3>
                                <button className="ad-modal-close" onClick={closeRejectModal}>
                                    <HiOutlineXMark />
                                </button>
                            </div>
                            <div className="ad-modal-body">
                                <p>Please provide a reason for rejecting this result:</p>
                                <textarea
                                    value={rejectReason}
                                    onChange={(e) => setRejectReason(e.target.value)}
                                    placeholder="Enter reason for rejection..."
                                    rows="4"
                                />
                            </div>
                            <div className="ad-modal-footer">
                                <button className="ad-btn ad-btn-secondary" onClick={closeRejectModal}>
                                    Cancel
                                </button>
                                <button className="ad-btn ad-btn-danger" onClick={handleReject}>
                                    Reject Result
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}