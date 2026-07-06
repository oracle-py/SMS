import React, { useState, useEffect } from "react";
import "./drawer.css";
import api from "../../../api/axios";

import {
    HiOutlineXMark,
    HiOutlineUser,
    HiOutlineEnvelope,
    HiOutlinePhone,
    HiOutlineAcademicCap,
    HiOutlineIdentification,
    HiOutlineBookOpen
} from "react-icons/hi2";

export default function RegisterLecturerDrawer({ open, onClose }) {

    const initialData = {

        first_name: "",
        last_name: "",
        other_name: "",

        gender: "",

        email: "",
        phone: "",

        department: "",

        rank: "",

        employment_type: "full_time",

        staff_id: "",

        date_of_birth: "",

        auto_generate_staff_id: true,

        courses: []

    };

    const [formData, setFormData] = useState(initialData);
    const [departments, setDepartments] = useState([]);
    const [courses, setCourses] = useState([]);
    const [courseSearch, setCourseSearch] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (open) {
            fetchDepartments();
            fetchCourses();
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

    const fetchCourses = async () => {
        try {
            const response = await api.get('/courses/');
            setCourses(response.data.results || response.data);
        } catch (error) {
            console.error('Error fetching courses:', error);
        }
    };

    const selectedDepartment = departments.find(d => d.id === parseInt(formData.department));

    const filteredCourses = courses.filter(course => {
        const search = courseSearch.toLowerCase();

        return (
            course.course_code?.toLowerCase().includes(search) ||
            course.course_title?.toLowerCase().includes(search)
        );
    });

    function handleChange(e){

        const { name, value } = e.target;

        setFormData(prev=>({

            ...prev,

            [name]:value

        }));

    }

    const handleCourseToggle = (courseId) => {
        setFormData(prev => ({
            ...prev,
            courses: prev.courses.includes(courseId)
                ? prev.courses.filter(id => id !== courseId)
                : [...prev.courses, courseId]
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            const response = await api.post('/lecturers/', {
                user_data: {
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                    other_name: formData.other_name,
                    email: formData.email,
                    phone: formData.phone
                },
                gender: formData.gender,
                staff_id: formData.auto_generate_staff_id ? null : formData.staff_id,
                department: formData.department,
                rank: formData.rank,
                employment_type: formData.employment_type,
                date_of_birth: formData.date_of_birth,
                courses: formData.courses
            });
            
            alert('Lecturer registered successfully!');
            setFormData(initialData);
            onClose();
        } catch (error) {
            console.error('Error registering lecturer:', error);
            alert(`Error: ${error.response?.data || 'Failed to register lecturer'}`);
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

                    <span>LECTURER MANAGEMENT</span>

                    <h2>Register Lecturer</h2>

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

                {/* PERSONAL */}

                <section className="drawer-section">

                    <h3>

                        <HiOutlineUser/>

                        Personal Information

                    </h3>

                    <div className="drawer-grid">

                        <div className="drawer-input">

                            <label>First Name</label>

                            <input
                                name="first_name"
                                value={formData.first_name}
                                onChange={handleChange}
                            />

                        </div>

                        <div className="drawer-input">

                            <label>Last Name</label>

                            <input
                                name="last_name"
                                value={formData.last_name}
                                onChange={handleChange}
                            />

                        </div>

                        <div className="drawer-input">

                            <label>Other Name</label>

                            <input
                                name="other_name"
                                value={formData.other_name}
                                onChange={handleChange}
                            />

                        </div>

                        <div className="drawer-input">

                            <label>Gender</label>

                            <select
                                name="gender"
                                value={formData.gender}
                                onChange={handleChange}
                            >

                                <option value="">Select</option>

                                <option>Male</option>

                                <option>Female</option>

                            </select>

                        </div>

                    </div>

                </section>

                {/* CONTACT */}

                <section className="drawer-section">

                    <h3>

                        <HiOutlineEnvelope/>

                        Contact Information

                    </h3>

                    <div className="drawer-grid">

                        <div className="drawer-input">

                            <label>Email</label>

                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                            />

                        </div>

                        <div className="drawer-input">

                            <label>Phone</label>

                            <input
                                name="phone"
                                value={formData.phone}
                                onChange={handleChange}
                            />

                        </div>

                    </div>

                </section>

                {/* ACADEMIC */}

                <section className="drawer-section">

                    <h3>

                        <HiOutlineAcademicCap/>

                        Academic Details

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

                            <label>Academic Rank</label>

                            <select
                                name="rank"
                                value={formData.rank}
                                onChange={handleChange}
                            >

                                <option value="">Select Rank</option>

                                <option value="graduate_assistant">Graduate Assistant</option>

                                <option value="assistant_lecturer">Assistant Lecturer</option>

                                <option value="lecturer_ii">Lecturer II</option>

                                <option value="lecturer_i">Lecturer I</option>

                                <option value="senior_lecturer">Senior Lecturer</option>

                                <option value="associate_professor">Associate Professor</option>

                                <option value="professor">Professor</option>

                            </select>

                        </div>

                        <div className="drawer-input">

                            <label>Employment Type</label>

                            <select
                                name="employment_type"
                                value={formData.employment_type}
                                onChange={handleChange}
                            >

                                <option value="full_time">Full Time</option>

                                <option value="part_time">Part Time</option>

                                <option value="visiting">Visiting</option>

                                <option value="contract">Contract</option>

                            </select>

                        </div>

                        <div className="drawer-input">

                            <label>Date of Birth</label>

                            <input
                                type="date"
                                name="date_of_birth"
                                value={formData.date_of_birth}
                                onChange={handleChange}
                            />

                        </div>

                    </div>

                </section>

               {/* COURSE ASSIGNMENT */}

<section className="drawer-section">

    <h3>

        <HiOutlineBookOpen />

        Course Assignment

    </h3>

    <p className="drawer-hint">
        Select the courses this lecturer will be responsible for.
    </p>

    <div className="course-assignment-card">

        <div className="course-assignment-header">

            <div>

                <h4>Available Courses</h4>

                <span>

                    {formData.courses.length} selected

                </span>

            </div>

        </div>

        <div className="course-search">

            <input
                type="text"
                placeholder="Search course code or title..."
                value={courseSearch}
                onChange={(e)=>setCourseSearch(e.target.value)}
            />

        </div>

        <div className="course-list">

            {

                filteredCourses.length > 0

                ?

                filteredCourses.map(course=>(

                    <label

                        key={course.id}

                        className={`course-card ${
                            formData.courses.includes(course.id)
                                ? "selected"
                                : ""
                        }`}

                    >

                        <input

                            type="checkbox"

                            checked={formData.courses.includes(course.id)}

                            onChange={()=>handleCourseToggle(course.id)}

                        />

                        <div className="course-card-body">

                            <div className="course-code">

                                {course.course_code}

                            </div>

                            <div className="course-title">

                                {course.course_title}

                            </div>

                        </div>

                    </label>

                ))

                :

                <div className="drawer-empty">

                    No matching courses found.

                </div>

            }

        </div>

        {

            formData.courses.length > 0 &&

            <div className="selected-course-summary">

                <span>

                    Assigned Courses

                </span>

                <div className="selected-course-tags">

                    {

                        courses

                        .filter(course=>formData.courses.includes(course.id))

                        .map(course=>(

                            <span
                                key={course.id}
                                className="course-tag"
                            >

                                {course.course_code}

                            </span>

                        ))

                    }

                </div>

            </div>

        }

    </div>

</section>

                {/* ACCOUNT */}

                <section className="drawer-section">

                    <h3>

                        <HiOutlineIdentification/>

                        Lecturer Account

                    </h3>

                    <div className="drawer-switch">

                        <label>

                            <input
                                type="checkbox"
                                checked={formData.auto_generate_staff_id}
                                onChange={(e)=>setFormData({

                                    ...formData,

                                    auto_generate_staff_id:e.target.checked

                                })}
                            />

                            Automatically Generate Staff ID

                        </label>

                    </div>

                    {

                        !formData.auto_generate_staff_id &&

                        <div className="drawer-input">

                            <label>Staff ID</label>

                            <input
                                name="staff_id"
                                value={formData.staff_id}
                                onChange={handleChange}
                            />

                        </div>

                    }

                    <div className="preview-note">

                        <strong>Lecturer Login</strong>

                        <p>

                            Lecturer will log in using the registered Staff ID and create a password during first login.

                        </p>

                    </div>

                </section>

                {/* SUMMARY */}

                <section className="drawer-section">

                    <h3>Registration Summary</h3>

                    <div className="registration-summary">

                        <div>

                            <span>Name</span>

                            <strong>

                                {formData.first_name} {formData.last_name}

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

                            <span>Rank</span>

                            <strong>

                                {formData.rank || "--"}

                            </strong>

                        </div>

                        <div>

                            <span>Email</span>

                            <strong>

                                {formData.email || "--"}

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

                        Register Lecturer

                    </button>

                </div>

            </form>

        </aside>

        </>

    );

}