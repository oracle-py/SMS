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

function Teachers() {

    const [teachers,setTeachers]=useState([]);

    const [loading,setLoading]=useState(true);

    useEffect(()=>{

        fetchTeachers();

    },[]);

    async function fetchTeachers(){

        setLoading(true);

        try{

            const response=await api.get("/lecturers/");

            setTeachers(

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

                <div className="ad-hero-card">

                    <div>

                        <h1>

                            Lecturers Management

                        </h1>

                        <p>

                            Manage lecturers, departments and staff records.

                        </p>

                    </div>

                    <button className="ad-button-primary">

                        <HiOutlinePlus/>

                        Add Lecturer

                    </button>

                </div>

                <div className="ad-stat-strip">

                    <div>

                        <span>Total Lecturers</span>

                        <h2>

                            {teachers.length}

                        </h2>

                    </div>

                </div>

                {

                    loading

                    ?

                    <div className="ad-loading">

                        Loading lecturers...

                    </div>

                    :

                    <div className="ad-card">

                        <table className="ad-table lecturer-table">

                            <thead>

                                <tr>

                                    <th>Lecturer</th>

                                    <th>Staff ID</th>

                                    <th>Email</th>

                                    <th>Department</th>

                                    <th>Rank</th>

                                    <th>Status</th>

                                    <th></th>

                                </tr>

                            </thead>

                            <tbody>

                                {

                                    teachers.length>0

                                    ?

                                    teachers.map(teacher=>{

                                        const fullName=

                                        `${teacher.user?.first_name || ""} ${teacher.user?.last_name || ""}`;

                                        const initials=

                                        fullName

                                        .trim()

                                        .split(" ")

                                        .map(name=>name[0])

                                        .join("")

                                        .substring(0,2)

                                        .toUpperCase();

                                        return(

                                            <tr key={teacher.id}>

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

                                                                Lecturer

                                                            </span>

                                                        </div>

                                                    </div>

                                                </td>

                                                <td>

                                                    {teacher.staff_id}

                                                </td>

                                                <td>

                                                    {teacher.user?.email}

                                                </td>

                                                <td>

                                                    {

                                                        teacher.department_name ||

                                                        "—"

                                                    }

                                                </td>

                                                <td>

                                                    {

                                                        teacher.rank ||

                                                        "—"

                                                    }

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

                                            No lecturers found.

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

export default Teachers;