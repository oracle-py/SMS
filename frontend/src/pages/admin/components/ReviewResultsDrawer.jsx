import React, { useState, useEffect } from "react";
import "./drawer.css";

import {
    HiOutlineXMark,
    HiOutlineClipboardDocumentList,
    HiOutlineAcademicCap,
    HiOutlineUser,
    HiOutlineCheckCircle,
    HiOutlineXCircle,
    HiOutlineClock
} from "react-icons/hi2";

export default function ReviewResultsDrawer({ open, onClose }) {

    const [pendingGrades, setPendingGrades] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (open) {
            fetchPendingGrades();
        }
    }, [open]);

    const fetchPendingGrades = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/grades/?status=pending', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setPendingGrades(data.results || data);
            }
        } catch (error) {
            console.error('Error fetching pending grades:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (grade) => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`http://localhost:8001/api/v1/grades/${grade.id}/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: 'approved' })
            });
            if (response.ok) {
                fetchPendingGrades();
            }
        } catch (error) {
            console.error('Error approving grade:', error);
        }
    };

    const handleReject = async (grade) => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`http://localhost:8001/api/v1/grades/${grade.id}/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: 'rejected' })
            });
            if (response.ok) {
                fetchPendingGrades();
            }
        } catch (error) {
            console.error('Error rejecting grade:', error);
        }
    };

    if (!open) return null;

    return (

        <>

            <div
                className="drawer-overlay"
                onClick={onClose}
            />

            <aside className="drawer">

                <div className="drawer-header">

                    <div>

                        <span>RESULT MANAGEMENT</span>

                        <h2>Review Results</h2>

                    </div>

                    <button
                        className="drawer-close"
                        onClick={onClose}
                    >

                        <HiOutlineXMark/>

                    </button>

                </div>

                <div className="drawer-body">

                    {loading ? (
                        <div className="drawer-loading">Loading pending results...</div>
                    ) : pendingGrades.length === 0 ? (
                        <div className="drawer-empty">No pending results to review</div>
                    ) : (
                        pendingGrades.map((grade)=>(

                            <div
                                key={grade.id}
                                className="result-review-card"
                            >

                                <div className="result-review-header">

                                    <div>

                                        <h3>

                                            <HiOutlineClipboardDocumentList/>

                                            {grade.registration?.course?.course_code || 'N/A'}

                                        </h3>

                                        <p>

                                            {grade.registration?.course?.course_title || 'N/A'}

                                        </p>

                                    </div>

                                    <span className="pending-badge">

                                        <HiOutlineClock/>

                                        Pending

                                    </span>

                                </div>

                                <div className="result-review-grid">

                                    <div>

                                        <strong>

                                            <HiOutlineUser/>

                                            Lecturer

                                        </strong>

                                        <p>{grade.submitted_by ? `${grade.submitted_by.first_name} ${grade.submitted_by.last_name}` : 'Unknown'}</p>

                                    </div>

                                    <div>

                                        <strong>

                                            <HiOutlineAcademicCap/>

                                            Session

                                        </strong>

                                        <p>{grade.registration?.session?.name || 'N/A'}</p>

                                    </div>

                                    <div>

                                        <strong>

                                            Semester

                                        </strong>

                                        <p>{grade.registration?.semester?.get_name_display || 'N/A'}</p>

                                    </div>

                                    <div>

                                        <strong>

                                            Submitted

                                        </strong>

                                        <p>{grade.submitted_at ? new Date(grade.submitted_at).toLocaleDateString() : 'N/A'}</p>

                                    </div>

                                </div>

                                <div className="result-review-actions">

                                    <button
                                        className="review-btn reject"
                                        onClick={()=>handleReject(grade)}
                                    >

                                        <HiOutlineXCircle/>

                                        Reject

                                    </button>

                                    <button
                                        className="review-btn approve"
                                        onClick={()=>handleApprove(grade)}
                                    >

                                        <HiOutlineCheckCircle/>

                                        Approve

                                    </button>

                                </div>

                            </div>

                        ))
                    )}

                </div>

            </aside>

        </>

    );

}