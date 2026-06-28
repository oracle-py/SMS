import React, { useState, useEffect } from "react";
import "./drawer.css";

import {
    HiOutlineXMark,
    HiOutlineBookOpen,
    HiOutlineAcademicCap,
    HiOutlineBuildingOffice2,
    HiOutlineClipboardDocumentList
} from "react-icons/hi2";

export default function CreateCourseDrawer({ open, onClose }) {

    const initialData = {

        course_code:"",
        course_title:"",
        credit_units:"",
        semester:"",

        level:"",

        department:"",

        status:"Active"

    };

    const [formData,setFormData]=useState(initialData);
    const [departments, setDepartments] = useState([]);
    const [levels, setLevels] = useState([]);
    const [semesters, setSemesters] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (open) {
            fetchDepartments();
            fetchLevels();
            fetchSemesters();
        }
    }, [open]);

    const fetchDepartments = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/departments/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setDepartments(data.results || data);
            }
        } catch (error) {
            console.error('Error fetching departments:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchLevels = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/levels/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setLevels(data.results || data);
            }
        } catch (error) {
            console.error('Error fetching levels:', error);
        }
    };

    const fetchSemesters = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/semesters/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setSemesters(data.results || data);
            }
        } catch (error) {
            console.error('Error fetching semesters:', error);
        }
    };

    const selectedDepartment = departments.find(d => d.id === parseInt(formData.department));
    const selectedLevel = levels.find(l => l.id === parseInt(formData.level));
    const selectedSemester = semesters.find(s => s.id === parseInt(formData.semester));

    function handleChange(e){

        const {name,value}=e.target;

        setFormData(prev=>({

            ...prev,

            [name]:value

        }));

    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/courses/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    course_code: formData.course_code,
                    course_title: formData.course_title,
                    credit_unit: parseInt(formData.credit_units),
                    level_id: formData.level,
                    semester_id: formData.semester,
                    department: formData.department,
                    is_active: formData.status === 'Active'
                })
            });
            
            if (response.ok) {
                alert('Course created successfully!');
                onClose();
            } else {
                const error = await response.json();
                alert(`Error: ${JSON.stringify(error)}`);
            }
        } catch (error) {
            console.error('Error creating course:', error);
            alert('Failed to create course');
        }
    };

    if(!open) return null;

    return(

    <>

        <div
            className="drawer-overlay"
            onClick={onClose}
        />

        <aside className="drawer">

            <div className="drawer-header">

                <div>

                    <span>COURSE MANAGEMENT</span>

                    <h2>Create Course</h2>

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

                {/* COURSE */}

                <section className="drawer-section">

                    <h3>

                        <HiOutlineBookOpen/>

                        Course Information

                    </h3>

                    <div className="drawer-grid">

                        <div className="drawer-input">

                            <label>Course Code</label>

                            <input
                                name="course_code"
                                value={formData.course_code}
                                onChange={handleChange}
                                placeholder="CPE401"
                            />

                        </div>

                        <div className="drawer-input">

                            <label>Course Title</label>

                            <input
                                name="course_title"
                                value={formData.course_title}
                                onChange={handleChange}
                                placeholder="Computer Architecture"
                            />

                        </div>

                        <div className="drawer-input">

                            <label>Credit Units</label>

                            <select
                                name="credit_units"
                                value={formData.credit_units}
                                onChange={handleChange}
                            >

                                <option value="">Select</option>

                                <option>1</option>
                                <option>2</option>
                                <option>3</option>
                                <option>4</option>
                                <option>5</option>

                            </select>

                        </div>

                        <div className="drawer-input">

                            <label>Semester</label>

                            <select
                                name="semester"
                                value={formData.semester}
                                onChange={handleChange}
                            >

                                <option value="">Select Semester</option>

                                {semesters.map(semester => (
                                    <option key={semester.id} value={semester.id}>
                                        {semester.name_display || semester.name}
                                    </option>
                                ))}

                            </select>

                        </div>

                    </div>

                </section>

                {/* ACADEMIC */}

                <section className="drawer-section">

                    <h3>

                        <HiOutlineBuildingOffice2/>

                        Academic Information

                    </h3>

                    <div className="drawer-grid">

                        <div className="drawer-input">

                            <label>Department</label>

                            <select
                                name="department"
                                value={formData.department}
                                onChange={handleChange}
                                disabled={loading}
                            >

                                <option value="">{loading ? 'Loading departments...' : 'Select Department'}</option>

                                {departments.map(dept => (
                                    <option key={dept.id} value={dept.id}>
                                        {dept.name}
                                    </option>
                                ))}

                            </select>

                        </div>

                        <div className="drawer-input">

                            <label>Level</label>

                            <select
                                name="level"
                                value={formData.level}
                                onChange={handleChange}
                            >

                                <option value="">Select Level</option>

                                {levels.map(level => (
                                    <option key={level.id} value={level.id}>
                                        {level.name}
                                    </option>
                                ))}

                            </select>

                        </div>

                        <div className="drawer-input">

                            <label>Status</label>

                            <select
                                name="status"
                                value={formData.status}
                                onChange={handleChange}
                            >

                                <option>Active</option>

                                <option>Inactive</option>

                            </select>

                        </div>

                    </div>

                </section>

                {/* SUMMARY */}

                <section className="drawer-section">

                    <h3>

                        <HiOutlineClipboardDocumentList/>

                        Course Summary

                    </h3>

                    <div className="registration-summary">

                        <div>

                            <span>Course</span>

                            <strong>

                                {formData.course_code || "--"}

                            </strong>

                        </div>

                        <div>

                            <span>Title</span>

                            <strong>

                                {formData.course_title || "--"}

                            </strong>

                        </div>

                        <div>

                            <span>Department</span>

                            <strong>

                                {selectedDepartment?.name || "--"}

                            </strong>

                        </div>

                        <div>

                            <span>Faculty</span>

                            <strong>

                                {selectedDepartment?.faculty_name || "--"}

                            </strong>

                        </div>

                        <div>

                            <span>Level</span>

                            <strong>

                                {selectedLevel?.name || "--"}

                            </strong>

                        </div>

                        <div>

                            <span>Semester</span>

                            <strong>

                                {selectedSemester?.name_display || selectedSemester?.name || "--"}

                            </strong>

                        </div>

                    </div>

                </section>

                <div className="drawer-actions">

                    <button
                        type="button"
                        className="drawer-btn secondary"
                        onClick={onClose}
                    >

                        Cancel

                    </button>

                    <button
                        type="submit"
                        className="drawer-btn primary"
                    >

                        Create Course

                    </button>

                </div>

            </form>

        </aside>

    </>

    );

}