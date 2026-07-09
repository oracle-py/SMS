import React, { useState, useEffect } from "react";
import "./drawer.css";
import api from "../../../api/axios";

import {
    HiOutlineXMark,
    HiOutlineUser,
    HiOutlineAcademicCap,
    HiOutlineEnvelope,
    HiOutlinePhone,
    HiOutlineBuildingOffice2,
    HiOutlineIdentification,
    HiOutlineUserGroup
} from "react-icons/hi2";

export default function RegisterStudentDrawer({

    open,

    onClose

}){

    const initialData = {

        first_name:"",

        last_name:"",

        other_name:"",

        gender:"",

        date_of_birth:"",

        email:"",

        phone:"",

        academic_session:"",

        programme:"",

        entry_level:"",

        student_type:"",

        auto_generate_matric:true,

        matric_number:"",

        parent_first_name:"",

        parent_last_name:"",

        parent_email:"",

        parent_phone:"",

        parent_relationship:"guardian"

    };

    const [formData,setFormData]=useState(initialData);

    const [programmes, setProgrammes] = useState([]);
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (open) {
            fetchProgrammes();
            fetchSessions();
        }
    }, [open]);

    const fetchProgrammes = async () => {
        setLoading(true);
        try {
            const response = await api.get('/programmes/');
            setProgrammes(response.data.results || response.data);
        } catch (error) {
            // Silently handle error
        } finally {
            setLoading(false);
        }
    };

    const fetchSessions = async () => {
        try {
            const response = await api.get('/sessions/');
            // Filter to show only active sessions
            const allSessions = response.data.results || response.data;
            const activeSessions = allSessions.filter(session => session.is_active);
            setSessions(activeSessions);
            
            // Auto-select the active session if there's exactly one
            if (activeSessions.length === 1) {
                setFormData(prev => ({
                    ...prev,
                    academic_session: activeSessions[0].id
                }));
            }
        } catch (error) {
            console.error('Error fetching sessions:', error);
            setSessions([]);
        }
    };

    const selectedProgramme = programmes.find(p => p.id === parseInt(formData.programme));

    function handleChange(e){

        const{

            name,

            value

        }=e.target;

        setFormData(prev=>{

            const newData = {

                ...prev,

                [name]:value

            };

            // Auto-fill entry level based on student type
            if (name === 'student_type') {
                if (value === 'UTME') {
                    newData.entry_level = '100';
                } else if (value === 'Direct Entry') {
                    newData.entry_level = '200';
                } else if (value === 'Transfer') {
                    newData.entry_level = '300';
                }
            }

            return newData;

        });

    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const payload = {
                user_data: {
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                    other_name: formData.other_name,
                    email: formData.email,
                    phone: formData.phone
                },
                gender: formData.gender,
                date_of_birth: formData.date_of_birth,
                student_id: formData.auto_generate_matric ? null : formData.matric_number,
                grade_level: parseInt(formData.entry_level),
                programme: formData.programme
            };
            
            // Only include parent data if parent first name, last name, and email are provided
            if (formData.parent_first_name && formData.parent_last_name && formData.parent_email) {
                payload.parent_first_name = formData.parent_first_name;
                payload.parent_last_name = formData.parent_last_name;
                payload.parent_email = formData.parent_email;
                payload.parent_phone = formData.parent_phone || null;
                payload.parent_relationship = formData.parent_relationship || 'guardian';
            }
            
            const response = await api.post('/students/', payload);
            
            // Only close drawer and reset form on success
            alert('Student registered successfully!');
            setFormData(initialData);
            onClose();
        } catch (error) {
            // Handle specific error messages
            let errorMessage = 'Failed to register student';
            if (error.response?.data) {
                const errorData = error.response.data;
                
                // Check for duplicate email error
                if (errorData.user_data?.email) {
                    errorMessage = 'Email already exists. Please use a different email address.';
                }
                // Check for other user_data errors
                else if (errorData.user_data) {
                    const userErrors = Object.values(errorData.user_data).join(', ');
                    errorMessage = `Validation error: ${userErrors}`;
                }
                // Check for general errors
                else if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
                else if (errorData.error) {
                    errorMessage = errorData.error;
                }
                else if (typeof errorData === 'string') {
                    errorMessage = errorData;
                }
            }
            
            alert(`Error: ${errorMessage}`);
            // Do NOT close drawer or reset form on error
        } finally {
            setLoading(false);
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

                    <span>

                        STUDENT MANAGEMENT

                    </span>

                    <h2>

                        Register Student

                    </h2>

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

                {/* STUDENT INFORMATION */}

<section className="drawer-section">

    <h3>

        <HiOutlineUser/>

        Student Information

    </h3>

    <div className="drawer-grid">

        <div className="drawer-input">

            <label htmlFor="first_name">

                First Name

            </label>

            <input

                type="text"

                id="first_name"
                name="first_name"

                value={formData.first_name}

                onChange={handleChange}

                placeholder="John"
                autoComplete="given-name"

            />

        </div>

        <div className="drawer-input">

            <label htmlFor="last_name">

                Last Name

            </label>

            <input

                type="text"
                id="last_name"
                name="last_name"

                value={formData.last_name}

                onChange={handleChange}

                placeholder="Doe"
                autoComplete="family-name"

            />

        </div>

        <div className="drawer-input">

            <label htmlFor="other_name">

                Other Name

            </label>

            <input

                type="text"
                id="other_name"
                name="other_name"

                value={formData.other_name}

                onChange={handleChange}

                placeholder="Michael"
                autoComplete="additional-name"

            />

        </div>

        <div className="drawer-input">

            <label htmlFor="gender">

                Gender

            </label>

            <select

                id="gender"
                name="gender"

                value={formData.gender}

                onChange={handleChange}

            >

                <option value="">

                    Select Gender

                </option>

                <option value="Male">

                    Male

                </option>

                <option value="Female">

                    Female

                </option>

            </select>

        </div>

        <div className="drawer-input">

            <label htmlFor="date_of_birth">

                Date of Birth

            </label>

            <input

                type="date"
                id="date_of_birth"
                name="date_of_birth"

                value={formData.date_of_birth}

                onChange={handleChange}
                autoComplete="bday"

            />

        </div>

    </div>

</section>
                                {/* CONTACT INFORMATION */}

                <section className="drawer-section">

                    <h3>

                        <HiOutlineEnvelope/>

                        Contact Information

                    </h3>

                    <div className="drawer-grid">

                        <div className="drawer-input">

                            <label htmlFor="email">

                                Email Address

                            </label>

                            <input

                                type="email"
                                id="email"
                                name="email"

                                value={formData.email}

                                onChange={handleChange}

                                placeholder="student@school.edu"
                                autoComplete="email"

                            />

                        </div>

                        <div className="drawer-input">

                            <label htmlFor="phone">

                                Phone Number

                            </label>

                            <input

                                type="tel"
                                id="phone"
                                name="phone"

                                value={formData.phone}

                                onChange={handleChange}

                                placeholder="+234..."
                                autoComplete="tel"

                            />

                        </div>

                    </div>

                </section>

               {/* ACADEMIC INFORMATION */}

<section className="drawer-section">

    <h3>

        <HiOutlineAcademicCap/>

        Academic Information

    </h3>

    <div className="drawer-grid">

        <div className="drawer-input">

            <label htmlFor="academic_session">

                Academic Session

            </label>

            <select

                id="academic_session"
                name="academic_session"

                value={formData.academic_session}

                onChange={handleChange}

            >

                <option value="">

                    Select Session

                </option>

                {sessions.map(session => (
                    <option key={session.id} value={session.id}>
                        {session.name}
                    </option>
                ))}

            </select>

        </div>

        <div className="drawer-input">

            <label htmlFor="programme">

                Programme

            </label>

            <select

                id="programme"
                name="programme"

                value={formData.programme}

                onChange={handleChange}

                disabled={loading}

            >

                <option value="">

                    {loading ? 'Loading programmes...' : 'Select Programme'}

                </option>

                {programmes.map(programme => (
                    <option key={programme.id} value={programme.id}>
                        {programme.name}
                    </option>
                ))}

            </select>

        </div>

        <div className="drawer-input">

            <label htmlFor="entry_level">

                Entry Level

            </label>

            <select

                id="entry_level"
                name="entry_level"

                value={formData.entry_level}

                onChange={handleChange}

                disabled

                style={{ backgroundColor: '#f1f5f9', cursor: 'not-allowed' }}

            >

                <option value="">

                    Select Level

                </option>

                <option value="100">

                    100

                </option>

                <option value="200">

                    200 (Direct Entry)

                </option>

                <option value="300">

                    300 (Transfer)

                </option>

            </select>

        </div>

        <div className="drawer-input">

            <label htmlFor="student_type">

                Student Type

            </label>

            <select

                id="student_type"
                name="student_type"

                value={formData.student_type}

                onChange={handleChange}

            >

                <option value="">

                    Select Student Type

                </option>

                <option value="UTME">

                    UTME

                </option>

                <option value="Direct Entry">

                    Direct Entry

                </option>

                <option value="Transfer">

                    Transfer

                </option>

            </select>

        </div>

    </div>

    <div className="drawer-derived">

        <div>

            <label>

                Faculty

            </label>

            <div className="drawer-derived-box">

                {

                    selectedProgramme?.faculty_name

                    ? selectedProgramme.faculty_name

                    : "--"

                }

            </div>

        </div>

        <div>

            <label>

                Department

            </label>

            <div className="drawer-derived-box">

                {

                    selectedProgramme?.department_name

                    ? selectedProgramme.department_name

                    : "--"

                }

            </div>

        </div>

    </div>

</section>

                {/* PARENT INFORMATION */}

                <section className="drawer-section">

                    <h3>

                        <HiOutlineUserGroup/>

                        Parent Information

                    </h3>

                    <div className="drawer-grid">

                        <div className="drawer-input">

                            <label htmlFor="parent_first_name">

                                Parent First Name

                            </label>

                            <input

                                type="text"
                                id="parent_first_name"
                                name="parent_first_name"

                                value={formData.parent_first_name}

                                onChange={handleChange}

                                placeholder="First Name"
                                autoComplete="given-name"

                            />

                        </div>

                        <div className="drawer-input">

                            <label htmlFor="parent_last_name">

                                Parent Last Name

                            </label>

                            <input

                                type="text"
                                id="parent_last_name"
                                name="parent_last_name"

                                value={formData.parent_last_name}

                                onChange={handleChange}

                                placeholder="Last Name"
                                autoComplete="family-name"

                            />

                        </div>

                        <div className="drawer-input">

                            <label htmlFor="parent_email">

                                Parent Email

                            </label>

                            <input

                                type="email"
                                id="parent_email"
                                name="parent_email"

                                value={formData.parent_email}

                                onChange={handleChange}

                                placeholder="parent@email.com"
                                autoComplete="email"

                            />

                        </div>

                        <div className="drawer-input">

                            <label htmlFor="parent_phone">

                                Parent Phone

                            </label>

                            <input

                                type="tel"
                                id="parent_phone"
                                name="parent_phone"

                                value={formData.parent_phone}

                                onChange={handleChange}

                                placeholder="+234..."
                                autoComplete="tel"

                            />

                        </div>

                        <div className="drawer-input">

                            <label htmlFor="parent_relationship">

                                Relationship

                            </label>

                            <select

                                id="parent_relationship"
                                name="parent_relationship"

                                value={formData.parent_relationship}

                                onChange={handleChange}

                            >

                                <option value="father">

                                    Father

                                </option>

                                <option value="mother">

                                    Mother

                                </option>

                                <option value="guardian">

                                    Guardian

                                </option>

                            </select>

                        </div>

                    </div>

                </section>
                               {/* STUDENT ACCOUNT */}

<section className="drawer-section">

    <h3>

        <HiOutlineIdentification/>

        Student Account

    </h3>

    <div className="drawer-switch">

        <label htmlFor="auto_generate_matric">

            <input

                type="checkbox"

                id="auto_generate_matric"
                name="auto_generate_matric"

                checked={formData.auto_generate_matric}

                onChange={(e)=>

                    setFormData({

                        ...formData,

                        auto_generate_matric:e.target.checked

                    })

                }

            />

            Automatically Generate Matric Number

        </label>

    </div>

    {

        !formData.auto_generate_matric &&

        <div className="drawer-input">

            <label htmlFor="matric_number">

                Matric Number

            </label>

            <input

                type="text"
                id="matric_number"
                name="matric_number"

                value={formData.matric_number}

                onChange={handleChange}

                placeholder="UJ/25/CPE/001"
                autoComplete="off"

            />

        </div>

    }

    <div className="preview-note">

        <strong>

            Student Login

        </strong>

        <p>

            After registration, the student will activate the account using the registered name and matric number. A password will be created during the first login process.

        </p>

    </div>

</section>

                <section className="drawer-section">

    <h3>

        Registration Summary

    </h3>

    <div className="registration-summary">

        <div>

            <span>Student</span>

            <strong>

                {`${formData.first_name} ${formData.last_name}` || "--"}

            </strong>

        </div>

        <div>

            <span>Programme</span>

            <strong>{selectedProgramme?.name || "--"}</strong>

        </div>

        <div>

            <span>Faculty</span>

            <strong>

                {

                    selectedProgramme?.faculty_name

                    ? selectedProgramme.faculty_name

                    : "--"

                }

            </strong>

        </div>

        <div>

            <span>Department</span>

            <strong>

                {

                    selectedProgramme?.department_name

                    ? selectedProgramme.department_name

                    : "--"

                }

            </strong>

        </div>

        <div>

            <span>Entry Level</span>

            <strong>{formData.entry_level || "--"}</strong>

        </div>

        <div>

            <span>Parent</span>

            <strong>
                {formData.parent_first_name && formData.parent_last_name 
                    ? `${formData.parent_first_name} ${formData.parent_last_name}` 
                    : "--"}
            </strong>

        </div>

    </div>

</section>

                {/* ACTIONS */}

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

                        Register Student

                    </button>

                </div>

            </form>

        </aside>

        </>

    );

}







