import React, { useState, useEffect } from "react";
import "./drawer.css";

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

        student_type:"UTME",

        auto_generate_matric:true,

        matric_number:"",

        parent_name:"",

        parent_email:"",

        parent_phone:"",

        relationship:"Parent"

    };

    const [formData,setFormData]=useState(initialData);

    const [programmes, setProgrammes] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (open) {
            fetchProgrammes();
        }
    }, [open]);

    const fetchProgrammes = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/programmes/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setProgrammes(data.results || data);
            }
        } catch (error) {
            console.error('Error fetching programmes:', error);
        } finally {
            setLoading(false);
        }
    };

    const selectedProgramme = programmes.find(p => p.id === parseInt(formData.programme));

    function handleChange(e){

        const{

            name,

            value

        }=e.target;

        setFormData(prev=>({

            ...prev,

            [name]:value

        }));

    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://localhost:8001/api/v1/students/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
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
                })
            });
            
            if (response.ok) {
                alert('Student registered successfully!');
                setFormData(initialData);
                onClose();
            } else {
                const error = await response.json();
                alert(`Error: ${JSON.stringify(error)}`);
            }
        } catch (error) {
            console.error('Error registering student:', error);
            alert('Failed to register student');
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

                <option>

                    2025/2026

                </option>

                <option>

                    2026/2027

                </option>

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

            >

                <option value="">

                    Select Level

                </option>

                <option>

                    100

                </option>

                <option>

                    200 (Direct Entry)

                </option>

                <option>

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

                <option>

                    UTME

                </option>

                <option>

                    Direct Entry

                </option>

                <option>

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

                            <label htmlFor="parent_name">

                                Parent Name

                            </label>

                            <input

                                type="text"
                                id="parent_name"
                                name="parent_name"

                                value={formData.parent_name}

                                onChange={handleChange}

                                placeholder="Parent Full Name"
                                autoComplete="name"

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

                            <label htmlFor="relationship">

                                Relationship

                            </label>

                            <select

                                id="relationship"
                                name="relationship"

                                value={formData.relationship}

                                onChange={handleChange}

                            >

                                <option>

                                    Parent

                                </option>

                                <option>

                                    Father

                                </option>

                                <option>

                                    Mother

                                </option>

                                <option>

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

            <strong>{formData.parent_name || "--"}</strong>

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