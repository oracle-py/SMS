import React, { useState, useEffect } from "react";
import "./drawer.css";
import api from "../../../api/axios";

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
            fetchActiveSemesters();
        }
    }, [open]);

    const fetchDepartments = async () => {
        setLoading(true);
        try {
            const response = await api.get('/departments/');
            setDepartments(response.data.results || response.data);
        } catch (error) {
            console.error('Error fetching departments:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchLevels = async () => {
        try {
            const response = await api.get('/levels/');
            setLevels(response.data.results || response.data);
        } catch (error) {
            console.error('Error fetching levels:', error);
        }
    };

    const fetchActiveSemesters = async () => {
        try {
            // First get the active session
            const sessionResponse = await api.get('/sessions/?is_active=true');
            const activeSession = (sessionResponse.data.results || sessionResponse.data)[0];
            
            if (activeSession) {
                // Then fetch semesters for the active session only
                const semesterResponse = await api.get(`/semesters/?session_id=${activeSession.id}`);
                setSemesters(semesterResponse.data.results || semesterResponse.data);
            } else {
                // Fallback to all semesters if no active session
                const response = await api.get('/semesters/');
                setSemesters(response.data.results || response.data);
            }
        } catch (error) {
            console.error('Error fetching active semesters:', error);
            // Fallback to all semesters on error
            try {
                const response = await api.get('/semesters/');
                setSemesters(response.data.results || response.data);
            } catch (fallbackError) {
                console.error('Error fetching semesters:', fallbackError);
            }
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
        
        // Validate required fields
        if (!formData.course_code || !formData.course_title || !formData.credit_units || 
            !formData.level || !formData.semester) {
            alert('Please fill in all required fields');
            return;
        }
        
        try {
            const payload = {
                course_code: formData.course_code,
                course_title: formData.course_title,
                credit_unit: parseInt(formData.credit_units),
                level_id: parseInt(formData.level),
                semester_id: parseInt(formData.semester),
                is_active: formData.status === 'Active'
            };
            
            // Only include department_id if a department is selected
            if (formData.department) {
                payload.department_id = parseInt(formData.department);
            }
            
            const response = await api.post('/courses/', payload);
            
            alert('Course created successfully!');
            
            // Reset form to initial state
            setFormData(initialData);
            
            onClose();
        } catch (error) {
            console.error('Error creating course:', error);
            alert(`Error: ${error.response?.data || 'Failed to create course'}`);
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