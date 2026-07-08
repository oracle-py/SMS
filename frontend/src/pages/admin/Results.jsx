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
    HiOutlineChevronDown
} from "react-icons/hi2";
import "./admin.css";

export default function Results() {
    const [courseSubmissions, setCourseSubmissions] = useState([]);
    const [loading, setLoading] = useState(true);

    const [expandedCourseId, setExpandedCourseId] = useState(null);

    const [selectedCourse, setSelectedCourse] = useState(null);

    const [rejectReason, setRejectReason] = useState("");

    const [showRejectModal, setShowRejectModal] = useState(false);

    useEffect(() => {
        fetchResults();
    }, []);

   const fetchResults = async () => {
    setLoading(true);

    try {

        const response = await api.get("/results/");

        // Handle different response formats
        const resultsData = response.data.results || response.data || [];
        
        // Group results by course and lecturer to create course-level submissions
        const courseGroups = {};
        
        resultsData.forEach(result => {
            const courseKey = `${result.course.course_code}-${result.lecturer?.id || 'unknown'}`;
            
            if (!courseGroups[courseKey]) {
                courseGroups[courseKey] = {
                    courseCode: result.course.course_code,
                    courseTitle: result.course.course_title,
                    lecturer: result.lecturer ? `${result.lecturer.first_name} ${result.lecturer.last_name}` : 'Unknown',
                    lecturerId: result.lecturer?.id,
                    session: result.session.name,
                    semester: result.semester.name || result.semester,
                    submittedAt: result.submitted_at,
                    status: result.status,
                    studentResults: []
                };
            }
            
            // Add individual student result
            let studentName = 'Unknown';
            let matricNo = 'N/A';
            
            if (typeof result.student === 'object' && result.student !== null) {
                const firstName = result.student.user?.first_name || result.student.first_name || '';
                const lastName = result.student.user?.last_name || result.student.last_name || '';
                studentName = `${firstName} ${lastName}`.trim() || 'Unknown';
                matricNo = result.student.student_id || 'N/A';
            } else if (typeof result.student === 'string') {
                studentName = result.student;
            }
            
            courseGroups[courseKey].studentResults.push({
                id: result.id,
                studentName: studentName,
                matricNo: matricNo,
                caScore: result.ca_score,
                examScore: result.exam_score,
                totalScore: result.total_score,
                grade: result.grade,
                status: result.status
            });
            
            // Update submission time to be the most recent
            if (result.submitted_at > courseGroups[courseKey].submittedAt) {
                courseGroups[courseKey].submittedAt = result.submitted_at;
            }
        });
        
        // Convert to array and add unique IDs
        const courseSubmissionsArray = Object.values(courseGroups).map((group, index) => ({
            ...group,
            id: index,
            studentCount: group.studentResults.length
        }));

        setCourseSubmissions(courseSubmissionsArray);

    } catch (error) {

        console.error(error);

    } finally {

        setLoading(false);

    }
};

    const handleApprove = async (courseId) => {
        try {
            const course = courseSubmissions.find(c => c.id === courseId);
            if (!course) return;
            
            // Approve all student results in this course
            const approvePromises = course.studentResults.map(result => 
                api.post(`/results/${result.id}/approve/`)
            );
            
            await Promise.all(approvePromises);
            fetchResults();
            alert('Course results approved successfully.');
        } catch (error) {
            console.error('Error approving course results:', error);
            alert('Failed to approve course results. Please try again.');
        }
    };

    const handleReject = async () => {
        if (!selectedCourse || !rejectReason.trim()) {
            alert('Please provide a reason for rejection.');
            return;
        }

        try {
            const course = courseSubmissions.find(c => c.id === selectedCourse.id);
            if (!course) return;
            
            // Reject all student results in this course
            const rejectPromises = course.studentResults.map(result => 
                api.post(`/results/${result.id}/reject/`, {
                    remarks: rejectReason
                })
            );
            
            await Promise.all(rejectPromises);
            setShowRejectModal(false);
            setSelectedCourse(null);
            setRejectReason('');
            fetchResults();
            alert('Course results rejected successfully.');
        } catch (error) {
            console.error('Error rejecting course results:', error);
            alert('Failed to reject course results. Please try again.');
        }
    };

    const openRejectModal = (course) => {
        setSelectedCourse(course);
        setRejectReason('');
        setShowRejectModal(true);
    };

    const closeRejectModal = () => {
        setShowRejectModal(false);
        setSelectedCourse(null);
        setRejectReason('');
    };

    
    const getStatusBadge = (status) => {

    const map = {

        pending: {
            text: "Pending Review",
            className: "status pending",
            icon: HiOutlineClock
        },

        approved: {
            text: "Published",
            className: "status approved",
            icon: HiOutlineCheckCircle
        },

        rejected: {
            text: "Rejected",
            className: "status rejected",
            icon: HiOutlineXCircle
        }

    };

    const config = map[status] || map.pending;

    const Icon = config.icon;

    return (

        <span className={config.className}>

            <Icon />

            {config.text}

        </span>

    );

};

    return (
        <DashboardLayout userRole="admin">
            <div className="ad-page">
                <div className="students-header-box">

    <div className="students-header-content">

        <div className="students-header-icon">
            <HiOutlineClipboardDocumentList />
        </div>

        <div className="students-header-text">

            <h1>
                Results Management
            </h1>

            <p>
                Review, approve and publish lecturers' submitted course results.
            </p>

        </div>

    </div>

</div>

<div className="ad-stat-strip">

    <div>
        <span>Pending</span>
        <h2>
            {
                courseSubmissions.filter(
                    item => item.status === "pending"
                ).length
            }
        </h2>
    </div>

    <div>
        <span>Published</span>
        <h2>
            {
                courseSubmissions.filter(
                    item => item.status === "approved"
                ).length
            }
        </h2>
    </div>

    <div>
        <span>Rejected</span>
        <h2>
            {
                courseSubmissions.filter(
                    item => item.status === "rejected"
                ).length
            }
        </h2>
    </div>

    <div>
        <span>Total Submissions</span>
        <h2>{courseSubmissions.length}</h2>
    </div>

</div>

                {loading ? (
                    <div className="ad-loading">
                        <div className="ad-spinner"></div>
                        <p>Loading results...</p>
                    </div>
                ) : courseSubmissions.length === 0 ? (
                    <div className="ad-empty-state">
                        <HiOutlineClipboardDocumentList className="empty-icon" />
                        <h3>No results found</h3>
                        <p>No results have been submitted yet</p>
                    </div>
                ) : (
                    <div className="ad-table-container">
                        <table className="ad-table">
                            <thead>

    <tr>

        <th>Course</th>

        <th>Lecturer</th>

        <th>Status</th>

        <th>Submitted</th>

        <th style={{ width: "180px" }}>
            Actions
        </th>

    </tr>

</thead>
                            <tbody>

{courseSubmissions.map((course) => (

    <React.Fragment key={course.id}>

        <tr>

           <td>

    <div className="course-card-mini">

        <div className="course-avatar">

            {course.courseCode?.substring(0,2)}

        </div>

        <div>

            <div className="course-code">

                {course.courseCode}

            </div>

            <div className="course-title">

                {course.courseTitle}

            </div>

        </div>

    </div>

</td>

            <td>

    <div className="lecturer-mini-card">

        <div className="lecturer-avatar">

            {course.lecturer?.charAt(0)}

        </div>

        <div>

            <div className="lecturer-name">

                {course.lecturer}

            </div>

            <div className="lecturer-role">

                Course Lecturer

            </div>

        </div>

    </div>

</td>

            <td>

                {getStatusBadge(course.status)}

            </td>

            <td>

                {

                    course.submittedAt

                    ?

                    new Date(

                        course.submittedAt

                    ).toLocaleDateString()

                    :

                    "—"

                }

            </td>

            <td>

                <div className="ad-action-buttons">

                    <button

                        className="ad-btn"

                        onClick={()=>

                            setExpandedCourseId(

                                expandedCourseId===course.id

                                ?

                                null

                                :

                                course.id

                            )

                        }

                    >

                        <HiOutlineChevronDown className={`chevron-icon ${expandedCourseId===course.id ? 'is-open' : ''}`} />

                    </button>

                </div>

            </td>

        </tr>

        {

            expandedCourseId===course.id && (

                <tr>

                    <td colSpan="5">

                        <div className="submission-review-card">

    <div className="submission-review-header">

        <div>

            <h3>
                {course.courseCode} • {course.courseTitle}
            </h3>

            <p>

                Submitted by

                <strong>

                    {" "}
                    {course.lecturer}

                </strong>

            </p>

        </div>

    </div>


    <div className="submission-meta-grid">

        <div className="submission-meta-item">

            <span>Session</span>

            <strong>

                {course.session}

            </strong>

        </div>

        <div className="submission-meta-item">

            <span>Semester</span>

            <strong>

                {course.semester}

            </strong>

        </div>

        <div className="submission-meta-item">

            <span>Students</span>

            <strong>

                {course.studentCount}

            </strong>

        </div>

        <div className="submission-meta-item">

            <span>Submitted</span>

            <strong>

                {

                    course.submittedAt

                    ?

                    new Date(
                        course.submittedAt
                    ).toLocaleString()

                    :

                    "—"

                }

            </strong>

        </div>

    </div>


    <div className="submission-students-table">

        <table className="ad-table">

            <thead>

                <tr>

                    <th>Student Name</th>

                    <th>Matric No</th>

                    <th>CA Score</th>

                    <th>Exam Score</th>

                    <th>Total Score</th>

                    <th>Grade</th>

                    <th>Status</th>

                </tr>

            </thead>

            <tbody>

                {course.studentResults.map((student, index) => (

                    <tr key={student.id || index}>

                        <td>

                            <strong>{student.studentName}</strong>

                        </td>

                        <td>

                            {student.matricNo}

                        </td>

                        <td>

                            {student.caScore}

                        </td>

                        <td>

                            {student.examScore}

                        </td>

                        <td>

                            <strong>{student.totalScore}</strong>

                        </td>

                        <td>

                            {student.grade}

                        </td>

                        <td>

                            {getStatusBadge(student.status)}

                        </td>

                    </tr>

                ))}

            </tbody>

        </table>

    </div>


    {

        course.status==="pending" && (

            <div className="submission-review-footer">

    <div className="submission-review-note">

        <HiOutlineClipboardDocumentList />

        <div>

            <strong>Administrator Review</strong>

            <p>
                Carefully verify all submitted scores before publishing.
                Once approved, results become visible to students.
            </p>

        </div>

    </div>

    <div className="submission-review-actions">

        <button

            className="review-btn reject"

            onClick={() => openRejectModal(course)}

        >

            <HiOutlineXCircle />

            Reject Submission

        </button>

        <button

            className="review-btn approve"

            onClick={() => handleApprove(course.id)}

        >

            <HiOutlineCheckCircle />

            Approve & Publish

        </button>

    </div>

</div>

        )

    }

</div>

                    </td>

                </tr>

            )

        }

    </React.Fragment>

))}

</tbody>
                        </table>
                    </div>
                )}

               {/* ============================
    Reject Submission Modal
============================ */}

{showRejectModal && (

    <div
        className="ad-modal-overlay"
        onClick={closeRejectModal}
    >

        <div
            className="ad-modal premium-modal"
            onClick={(e)=>e.stopPropagation()}
        >

            <div className="premium-modal-header">

                <div className="premium-modal-icon">

                    <HiOutlineXCircle />

                </div>

                <div>

                    <h2>

                        Reject Result Submission

                    </h2>

                    <p>

                        This submission will be returned to the lecturer for correction.

                    </p>

                </div>

                <button
                    className="premium-close-btn"
                    onClick={closeRejectModal}
                >

                    <HiOutlineXMark />

                </button>

            </div>

            <div className="premium-modal-body">

                <div className="review-course-summary">

                    <span>

                        Course

                    </span>

                    <strong>

                        {selectedCourse?.courseCode}

                        {" — "}

                        {selectedCourse?.courseTitle}

                    </strong>

                </div>

                <div className="review-course-summary">

                    <span>

                        Lecturer

                    </span>

                    <strong>

                        {selectedCourse?.lecturer}

                    </strong>

                </div>

                <div className="review-course-summary">

                    <span>

                        Number of Students

                    </span>

                    <strong>

                        {selectedCourse?.studentCount}

                    </strong>

                </div>

                <div className="review-divider"></div>

                <label className="reject-label">

                    Rejection Remarks

                </label>

                <textarea

                    rows={6}

                    value={rejectReason}

                    onChange={(e)=>setRejectReason(e.target.value)}

                    placeholder="Explain clearly why this submission is being rejected..."

                />

                <div className="reject-tip">

                    <HiOutlineClipboardDocumentList />

                    Provide enough information for the lecturer to make the necessary corrections before resubmitting.

                </div>

            </div>

            <div className="premium-modal-footer">

                <button

                    className="ad-btn ad-btn-secondary"

                    onClick={closeRejectModal}

                >

                    Cancel

                </button>

                <button

                    className="ad-btn ad-btn-danger"

                    onClick={handleReject}

                >

                    Reject Submission

                </button>

            </div>

        </div>

    </div>

)}
            </div>
        </DashboardLayout>
    );
}