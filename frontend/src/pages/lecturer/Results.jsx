import { useState, useEffect } from "react";
import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import {
    HiOutlineAcademicCap,
    HiOutlineUsers,
    HiOutlineCheckCircle,
    HiOutlineChevronDown,
    HiOutlineClock,
    HiOutlineArrowUturnLeft,
    HiOutlinePaperAirplane
} from "react-icons/hi2";
import "./Lecturer.css";

function initialsOf(student) {
    const first = student.user?.first_name?.charAt(0) || "";
    const last = student.user?.last_name?.charAt(0) || "";
    return `${first}${last}`.toUpperCase() || "?";
}

export default function Results() {

    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);

    const [expandedIds, setExpandedIds] = useState(new Set());

    // scores keyed by `${courseId}-${studentId}` -> { ca, exam }
    const [scores, setScores] = useState({});

    // per-course status: 'draft' | 'submitted' | 'published' | 'returned'
    // Note: Backend uses 'pending' for both draft and submitted, we distinguish by submitted_at
    const [courseStatus, setCourseStatus] = useState({});
    const [returnReasons, setReturnReasons] = useState({});

    const [savingId, setSavingId] = useState(null);
    const [submittingId, setSubmittingId] = useState(null);

    useEffect(() => {
        fetchCourses();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    async function fetchCourses() {

        setLoading(true);

        try {

            const userResponse = await api.get("/auth/me/");

            if (!userResponse.data?.data?.profile) {
                console.error("No profile data found in response");
                setCourses([]);
                return;
            }

            const assignedCourses = userResponse.data.data.profile.courses || [];

            const populatedCourses = await Promise.all(
                assignedCourses.map(async course => {

                    try {

                        const [registrationsRes, resultsRes] = await Promise.all([
                            api.get("/registrations/", { 
                                params: { 
                                    course: course.id,
                                    session: course.session_id,
                                    semester: course.semester_id
                                } 
                            }),
                            api.get("/results/", { params: { course: course.id } }).catch(() => null)
                        ]);

                        const registrations = registrationsRes.data.results || registrationsRes.data || [];
                        const students = registrations.map(reg => reg.student).filter(Boolean);

                        // Pre-fill any previously saved/submitted scores and status for this course
                        const existingResults = resultsRes?.data?.results || resultsRes?.data || [];

                        return { ...course, students, existingResults };
                    }
                    catch (courseError) {
                        console.error(`Error fetching students for course ${course.id}:`, courseError);
                        return { ...course, students: [], existingResults: [] };
                    }
                })
            );

            // Seed scores + status state from whatever the backend already has on file
            const seededScores = {};
            const seededStatus = {};
            const seededReasons = {};

            populatedCourses.forEach(course => {

                let courseHasAny = false;
                let overallStatus = "draft";
                let reason = null;

                (course.existingResults || []).forEach(result => {

                    const key = `${course.id}-${result.student_id || result.student}`;
                    seededScores[key] = {
                        ca: result.ca_score ?? "",
                        exam: result.exam_score ?? ""
                    };

                    // Determine status based on backend data
                    if (result.status === 'approved') {
                        overallStatus = 'published';
                        courseHasAny = true;
                    } else if (result.status === 'rejected') {
                        overallStatus = 'returned';
                        courseHasAny = true;
                        reason = result.remarks || "Rejected by admin";
                    } else if (result.submitted_at) {
                        overallStatus = 'submitted';
                        courseHasAny = true;
                    } else if (result.status === 'pending') {
                        overallStatus = 'draft';
                        courseHasAny = true;
                    }
                });

                if (courseHasAny) {
                    seededStatus[course.id] = overallStatus;
                    if (reason) seededReasons[course.id] = reason;
                }
            });

            setScores(prev => ({ ...seededScores, ...prev }));
            setCourseStatus(prev => ({ ...seededStatus, ...prev }));
            setReturnReasons(prev => ({ ...seededReasons, ...prev }));
            setCourses(populatedCourses);
        }
        catch (error) {
            console.error("Error fetching courses:", error);
            setCourses([]);
        }
        finally {
            setLoading(false);
        }
    }

    function toggleExpand(courseId) {
        setExpandedIds(prev => {
            const next = new Set(prev);
            if (next.has(courseId)) {
                next.delete(courseId);
            } else {
                next.add(courseId);
            }
            return next;
        });
    }

    function getStatus(courseId) {
        return courseStatus[courseId] || "draft";
    }

    function isLocked(courseId) {
        // Inputs are locked once results are awaiting admin review or already published.
        // A "returned" or "rejected" course unlocks again so the lecturer can fix and resubmit.
        const status = getStatus(courseId);
        return status === "submitted" || status === "published" || status === "approved";
    }

    function getScore(courseId, studentId, field) {
        const key = `${courseId}-${studentId}`;
        return scores[key]?.[field] ?? "";
    }

    function setScore(courseId, studentId, field, value) {

        if (value !== "" && Number(value) < 0) return;
        if (field === "ca" && Number(value) > 40) return;
        if (field === "exam" && Number(value) > 60) return;

        const key = `${courseId}-${studentId}`;
        setScores(prev => ({
            ...prev,
            [key]: { ...prev[key], [field]: value }
        }));
    }

    function getCompletionSummary(course) {

        let complete = 0;
        let started = 0;

        course.students.forEach(student => {
            const key = `${course.id}-${student.id}`;
            const entry = scores[key];
            const hasCa = entry?.ca !== undefined && entry?.ca !== "";
            const hasExam = entry?.exam !== undefined && entry?.exam !== "";

            if (hasCa && hasExam) complete += 1;
            else if (hasCa || hasExam) started += 1;
        });

        return { complete, started, total: course.students.length };
    }

    function buildResultsPayload(course) {
        return course.students
            .map(student => {
                const key = `${course.id}-${student.id}`;
                const entry = scores[key];
                if (!entry || (entry.ca === "" && entry.exam === "")) return null;

                return {
                    student_id: student.id,
                    course_id: course.id,
                    ca_score: entry.ca === "" ? null : Number(entry.ca),
                    exam_score: entry.exam === "" ? null : Number(entry.exam)
                };
            })
            .filter(Boolean);
    }

    async function handleSaveDraft(course) {

        const results = buildResultsPayload(course);

        if (results.length === 0) {
            alert("Enter at least one score before saving.");
            return;
        }

        setSavingId(course.id);

        try {

            await api.post("/results/batch/", {
                course_id: course.id,
                action: "save",
                results
            });

            setCourseStatus(prev => ({ ...prev, [course.id]: "draft" }));
            alert("Draft saved. You can come back and finish it later.");
        }
        catch (error) {
            console.error(error);
            alert("Unable to save draft. Please try again.");
        }
        finally {
            setSavingId(null);
        }
    }

    async function handleSubmit(course) {

        const allComplete = course.students.every(student => {
            const key = `${course.id}-${student.id}`;
            const entry = scores[key];
            return entry?.ca !== undefined && entry?.ca !== "" &&
                   entry?.exam !== undefined && entry?.exam !== "";
        });

        if (!allComplete) {
            alert("Please enter both CA and exam scores for every student before submitting.");
            return;
        }

        const results = buildResultsPayload(course);

        setSubmittingId(course.id);

        try {

            await api.post("/results/batch/", {
                course_id: course.id,
                action: "submit",
                results
            });

            setCourseStatus(prev => ({ ...prev, [course.id]: "submitted" }));
            setReturnReasons(prev => {
                const next = { ...prev };
                delete next[course.id];
                return next;
            });
            alert("Results submitted for admin approval.");
        }
        catch (error) {
            console.error(error);
            alert("Unable to submit results. Please try again.");
        }
        finally {
            setSubmittingId(null);
        }
    }

    const totalStudents = new Set();
    courses.forEach(course => {
        if (course.students && Array.isArray(course.students)) {
            course.students.forEach(student => {
                if (student && student.id) {
                    totalStudents.add(student.id);
                }
            });
        }
    });
    const uniqueStudentCount = totalStudents.size;

    return (
        <DashboardLayout userRole="lecturer">

            <div className="att-page">

                <div className="att-page-header">
                    <div>
                        <h1>Student Results</h1>
                        <p>Pick a course, enter CA and exam scores, then submit for admin approval.</p>
                    </div>

                    {!loading && courses.length > 0 && (
                        <div className="att-summary-pill">
                            <HiOutlineUsers />
                            {uniqueStudentCount} students · {courses.length} course{courses.length === 1 ? "" : "s"}
                        </div>
                    )}
                </div>

                {loading ? (

                    <div className="att-state-card">
                        <div className="att-spinner" />
                        <p>Loading your courses…</p>
                    </div>

                ) : courses.length === 0 ? (

                    <div className="att-state-card">
                        <HiOutlineAcademicCap className="att-empty-icon" />
                        <h3>No courses assigned</h3>
                        <p>You currently have no assigned courses.</p>
                    </div>

                ) : (

                    <div className="att-card-list">

                        {courses.map(course => {

                            const isOpen = expandedIds.has(course.id);
                            const summary = getCompletionSummary(course);
                            const status = getStatus(course.id);
                            const locked = isLocked(course.id);
                            const isSaving = savingId === course.id;
                            const isSubmitting = submittingId === course.id;

                            const allComplete = course.students.length > 0 &&
                                course.students.every(student => {
                                    const key = `${course.id}-${student.id}`;
                                    const entry = scores[key];
                                    return entry?.ca !== undefined && entry?.ca !== "" &&
                                           entry?.exam !== undefined && entry?.exam !== "";
                                });

                            return (
                                <div
                                    key={course.id}
                                    className={`att-card ${isOpen ? "is-open" : ""}`}
                                >

                                    <button
                                        type="button"
                                        className="att-card-header"
                                        onClick={() => toggleExpand(course.id)}
                                        aria-expanded={isOpen}
                                    >

                                        <div className="att-card-title">

                                            <span className="att-course-code">
                                                {course.course_code || course.code}
                                            </span>

                                            <div className="att-card-title-text">
                                                <h2>{course.course_title || course.title}</h2>
                                                <p>
                                                    Level {course.level?.name || course.level} ·{" "}
                                                    {course.students.length} student
                                                    {course.students.length === 1 ? "" : "s"}
                                                </p>
                                            </div>

                                        </div>

                                        <div className="att-card-header-right">

                                            <span className={`res-status-pill res-status-${status}`}>
                                                {status === "draft" && summary.complete === 0 && summary.started === 0
                                                    ? "Not started"
                                                    : status === "draft"
                                                    ? `${summary.complete}/${summary.total} complete`
                                                    : status === "submitted"
                                                    ? "Pending admin review"
                                                    : status === "published"
                                                    ? "Published"
                                                    : "Returned"}
                                            </span>

                                            <HiOutlineChevronDown className="att-chevron" />

                                        </div>

                                    </button>

                                    <div className="att-card-body-wrapper">
                                        <div className="att-card-body">

                                            <div className="att-toolbar">

                                                <div className="res-status-note-wrap">
                                                    {status === "submitted" && (
                                                        <div className="res-status-note res-note-pending">
                                                            <HiOutlineClock />
                                                            Submitted — awaiting admin approval.
                                                        </div>
                                                    )}

                                                    {status === "published" && (
                                                        <div className="res-status-note res-note-published">
                                                            <HiOutlineCheckCircle />
                                                            Published — results are now visible to students.
                                                        </div>
                                                    )}

                                                    {status === "returned" && (
                                                        <div className="res-status-note res-note-returned">
                                                            <HiOutlineArrowUturnLeft />
                                                            Your results were returned{returnReasons[course.id] ? `: ${returnReasons[course.id]}` : "."} Please review and resubmit.
                                                        </div>
                                                    )}
                                                    {status === "rejected" && (
                                                        <div className="res-status-note res-note-returned">
                                                            <HiOutlineArrowUturnLeft />
                                                            Your results were rejected{returnReasons[course.id] ? `: ${returnReasons[course.id]}` : "."} Please review and resubmit.
                                                        </div>
                                                    )}
                                                </div>

                                                <div className="res-toolbar-actions">

                                                    <button
                                                        type="button"
                                                        className="att-publish-btn res-save-btn"
                                                        onClick={() => handleSaveDraft(course)}
                                                        disabled={isSaving || isSubmitting || course.students.length === 0 || locked}
                                                    >
                                                        {isSaving ? "Saving…" : "Save"}
                                                    </button>

                                                    <button
                                                        type="button"
                                                        className="att-publish-btn"
                                                        onClick={() => handleSubmit(course)}
                                                        disabled={isSubmitting || isSaving || course.students.length === 0 || locked || !allComplete}
                                                    >
                                                        <HiOutlinePaperAirplane className="res-submit-icon" />
                                                        {isSubmitting
                                                            ? "Submitting…"
                                                            : status === "returned"
                                                            ? "Resubmit"
                                                            : "Submit"}
                                                    </button>

                                                </div>

                                            </div>

                                            {course.students.length === 0 ? (

                                                <div className="att-empty-row">
                                                    No students registered for this course.
                                                </div>

                                            ) : (

                                                <div className="att-single-list">

                                                    <h3>Enter results</h3>

                                                    <ul>
                                                        {course.students.map(student => (
                                                            <li key={student.id}>

                                                                <div className="att-student-info">
                                                                    <div className="att-avatar">
                                                                        {initialsOf(student)}
                                                                    </div>
                                                                    <div className="att-roster-text">
                                                                        <strong>
                                                                            {student.user?.first_name}{" "}
                                                                            {student.user?.last_name}
                                                                        </strong>
                                                                        <span>
                                                                            {student.student_id || student.id}
                                                                        </span>
                                                                    </div>
                                                                </div>

                                                                <div className="res-score-fields">

                                                                    <label className="res-score-field">
                                                                        <span>CA (0–40)</span>
                                                                        <input
                                                                            type="number"
                                                                            min="0"
                                                                            max="40"
                                                                            placeholder="CA"
                                                                            className="res-score-input"
                                                                            value={getScore(course.id, student.id, "ca")}
                                                                            onChange={(e) =>
                                                                                setScore(course.id, student.id, "ca", e.target.value)
                                                                            }
                                                                            disabled={locked}
                                                                        />
                                                                    </label>

                                                                    <label className="res-score-field">
                                                                        <span>Exam (0–60)</span>
                                                                        <input
                                                                            type="number"
                                                                            min="0"
                                                                            max="60"
                                                                            placeholder="Exam"
                                                                            className="res-score-input"
                                                                            value={getScore(course.id, student.id, "exam")}
                                                                            onChange={(e) =>
                                                                                setScore(course.id, student.id, "exam", e.target.value)
                                                                            }
                                                                            disabled={locked}
                                                                        />
                                                                    </label>

                                                                </div>

                                                            </li>
                                                        ))}
                                                    </ul>

                                                </div>

                                            )}

                                        </div>
                                    </div>

                                </div>
                            );
                        })}

                    </div>

                )}

            </div>

        </DashboardLayout>
    );
}
