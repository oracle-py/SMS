import { useState, useEffect } from "react";

import {
    HiOutlinePencil,
    HiOutlineTrash,
    HiOutlinePlus,
    HiOutlineUserCircle
} from "react-icons/hi2";

import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";

import "./admin.css";

function Students() {

    const [students,setStudents]=useState([]);

    const [loading,setLoading]=useState(true);

    useEffect(()=>{

        fetchStudents();

    },[]);

    async function fetchStudents(){

        setLoading(true);

        try{

            const response=await api.get("/students/");

            setStudents(

                response.data.results ||

                response.data

            );

        }

        catch(error){

            console.error(error);

        }

        finally{

            setLoading(false);

        }

    }

    return(

        <DashboardLayout>

            <div className="ad-page">

                <div className="ad-page-header">

                    <div>

                        <h1>

                            Students

                        </h1>

                        <p>

                            Manage registered students across the institution.

                        </p>

                    </div>

                    <button className="ad-button-primary">

                        <HiOutlinePlus/>

                        Add Student

                    </button>

                </div>

                <div className="ad-stat-strip">

                    <div>

                        <span>Total Students</span>

                        <h2>

                            {students.length}

                        </h2>

                    </div>

                </div>

                {

                    loading

                    ?

                    <div className="ad-loading">

                        Loading students...

                    </div>

                    :

                    <div className="ad-card">

                        <table className="ad-table">

                            <thead>

                                <tr>

                                    <th>Student</th>

                                    <th>Student ID</th>

                                    <th>Email</th>

                                    <th>Programme</th>

                                    <th>Level</th>

                                    <th>Status</th>

                                    <th></th>

                                </tr>

                            </thead>

                            <tbody>

                                {

                                    students.length>0

                                    ?

                                    students.map(student=>{

                                        const fullName=

                                        `${student.user?.first_name || ""} ${student.user?.last_name || ""}`;

                                        const initials=

                                        fullName

                                        .trim()

                                        .split(" ")

                                        .map(n=>n[0])

                                        .join("")

                                        .substring(0,2)

                                        .toUpperCase();

                                        return(

                                            <tr

                                                key={student.id}

                                            >

                                                <td>

                                                    <div className="ad-student">

                                                        <div className="ad-avatar">

                                                            {

                                                                initials ||

                                                                <HiOutlineUserCircle/>

                                                            }

                                                        </div>

                                                        <div>

                                                            <h4>

                                                                {fullName}

                                                            </h4>

                                                            <span>

                                                                Student

                                                            </span>

                                                        </div>

                                                    </div>

                                                </td>

                                                <td>

                                                    {student.student_id}

                                                </td>

                                                <td>

                                                    {student.user?.email}

                                                </td>

                                                <td>

                                                    {

                                                        student.programme_name ||

                                                        "—"

                                                    }

                                                </td>

                                                <td>

                                                    {

                                                        student.grade_level

                                                    }00 Level

                                                </td>

                                                <td>

                                                    <span className="ad-status">

                                                        Active

                                                    </span>

                                                </td>

                                                <td>

                                                    <div className="ad-action-buttons">

                                                        <button>

                                                            <HiOutlinePencil/>

                                                        </button>

                                                        <button>

                                                            <HiOutlineTrash/>

                                                        </button>

                                                    </div>

                                                </td>

                                            </tr>

                                        );

                                    })

                                    :

                                    <tr>

                                        <td

                                            colSpan="7"

                                            className="ad-empty-state"

                                        >

                                            No students have been added.

                                        </td>

                                    </tr>

                                }

                            </tbody>

                        </table>

                    </div>

                }

            </div>

        </DashboardLayout>

    );

}

export default Students;