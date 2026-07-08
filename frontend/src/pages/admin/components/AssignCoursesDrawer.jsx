import React, { useState } from "react";
import "./drawer.css";
import api from "../../../api/axios";

import {
    HiOutlineXMark,
    HiOutlineAcademicCap,
    HiOutlineUser,
    HiOutlineUsers,
    HiOutlineSquares2X2
} from "react-icons/hi2";

export default function AssignCoursesDrawer({ open, onClose }) {

    const initialData = {
        assignment_type: "student",
        student_id: "",
        grade_level: ""
    };

    const [formData, setFormData] = useState(initialData);
    const [loading, setLoading] = useState(false);

    function handleChange(e) {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            let endpoint;
            let data = {};

            if (formData.assignment_type === "student") {
                if (!formData.student_id || !formData.grade_level) {
                    alert("Please provide both the student's matric number and level.");
                    setLoading(false);
                    return;
                }

                endpoint = "courses/assign-level-to-student/";
                data = {
                    student_id: formData.student_id,
                    grade_level: parseInt(formData.grade_level)
                };
            } else if (formData.assignment_type === "level") {
                if (!formData.grade_level) {
                    alert("Please select a level.");
                    setLoading(false);
                    return;
                }

                endpoint = "courses/assign-to-level/";
                data = {
                    grade_level: parseInt(formData.grade_level)
                };
            } else {
                endpoint = "courses/assign-to-all/";
                data = {};
            }

            const response = await api.post(endpoint, data);

            if (response.data.success) {
                alert(response.data.message);
                setFormData(initialData);
                onClose();
            } else {
                alert(response.data.error || "Assignment failed.");
            }
        } catch (error) {
            const errorMessage = error.response?.data?.error || 
                                error.response?.data?.message ||
                                "Something went wrong while assigning courses.";
            alert(`Error: ${errorMessage}`);
        } finally {
            setLoading(false);
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
                        <span>COURSE MANAGEMENT</span>
                        <h2>Assign Courses</h2>
                    </div>
                    <button
                        className="drawer-close"
                        onClick={onClose}
                    >
                        <HiOutlineXMark/>
                    </button>
                </div>

                <form
                    className="drawer-body"
                    onSubmit={handleSubmit}
                >
                    {/* ASSIGNMENT TYPE */}
                    <section className="drawer-section">
                        <h3>
                            <HiOutlineAcademicCap/>
                            Assignment Type
                        </h3>
                        <div className="drawer-grid">
                            <div className="drawer-input">
                                <label>Assignment Type</label>
                                <select
                                    name="assignment_type"
                                    value={formData.assignment_type}
                                    onChange={handleChange}
                                >
                                    <option value="student">Individual Student</option>
                                    <option value="level">Specific Level</option>
                                    <option value="all">All Students</option>
                                </select>
                            </div>
                        </div>
                    </section>

                    {/* STUDENT DETAILS */}
                    {formData.assignment_type === "student" && (
                        <section className="drawer-section">
                            <h3>
                                <HiOutlineUser/>
                                Student Details
                            </h3>
                            <div className="drawer-grid">
                                <div className="drawer-input">
                                    <label>Student Matric Number</label>
                                    <input
                                        type="text"
                                        name="student_id"
                                        value={formData.student_id}
                                        onChange={handleChange}
                                        placeholder="e.g. 2026/NS/001"
                                    />
                                </div>
                                <div className="drawer-input">
                                    <label>Academic Level</label>
                                    <select
                                        name="grade_level"
                                        value={formData.grade_level}
                                        onChange={handleChange}
                                    >
                                        <option value="">Select Level</option>
                                        <option value="100">100 Level</option>
                                        <option value="200">200 Level</option>
                                        <option value="300">300 Level</option>
                                        <option value="400">400 Level</option>
                                        <option value="500">500 Level</option>
                                    </select>
                                </div>
                            </div>
                        </section>
                    )}

                    {/* LEVEL DETAILS */}
                    {formData.assignment_type === "level" && (
                        <section className="drawer-section">
                            <h3>
                                <HiOutlineSquares2X2/>
                                Level Details
                            </h3>
                            <div className="drawer-grid">
                                <div className="drawer-input">
                                    <label>Academic Level</label>
                                    <select
                                        name="grade_level"
                                        value={formData.grade_level}
                                        onChange={handleChange}
                                    >
                                        <option value="">Select Level</option>
                                        <option value="100">100 Level</option>
                                        <option value="200">200 Level</option>
                                        <option value="300">300 Level</option>
                                        <option value="400">400 Level</option>
                                        <option value="500">500 Level</option>
                                    </select>
                                </div>
                            </div>
                        </section>
                    )}

                    {/* ALL STUDENTS INFO */}
                    {formData.assignment_type === "all" && (
                        <section className="drawer-section">
                            <h3>
                                <HiOutlineUsers/>
                                All Students
                            </h3>
                            <div className="drawer-grid">
                                <div className="drawer-input">
                                    <p>
                                        This will assign courses to all eligible students based on their academic levels. 
                                        Each student will receive all courses assigned to their level.
                                    </p>
                                </div>
                            </div>
                        </section>
                    )}

                    <div className="drawer-footer">
                        <button
                            type="button"
                            className="drawer-cancel-btn"
                            onClick={onClose}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="drawer-submit-btn"
                            disabled={loading}
                        >
                            {loading ? "Assigning..." : "Assign Courses"}
                        </button>
                    </div>
                </form>
            </aside>
        </>
    );
}
