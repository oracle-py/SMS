import { useState, useEffect } from "react";

import {
    HiOutlineTrash,
    HiOutlinePlus,
    HiOutlineUserCircle
} from "react-icons/hi2";

import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import { useDashboardRefresh } from "../../context/DashboardContext";
import RegisterLecturerDrawer from "./components/RegisterLecturerDrawer";

import "./admin.css";

function Teachers() {

    const { refreshDashboard } = useDashboardRefresh();

    const [teachers,setTeachers]=useState([]);

    const [loading,setLoading]=useState(true);

    const [drawerOpen, setDrawerOpen] = useState(false);

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

    const handleDrawerClose = () => {
        setDrawerOpen(false);
        fetchTeachers();
        refreshDashboard();
    };

    const handleDelete = async (teacherId) => {
        if (!window.confirm('Are you sure you want to delete this lecturer?')) {
            return;
        }
        try {
            await api.delete(`/lecturers/${teacherId}/`);
            fetchTeachers();
            refreshDashboard();
        } catch (error) {
            console.error('Error deleting lecturer:', error);
            alert('Failed to delete lecturer');
        }
    };

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

                    <button className="ad-button-primary" onClick={() => setDrawerOpen(true)}>

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

                                                        <button onClick={() => handleDelete(teacher.id)}>

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

                <RegisterLecturerDrawer 
                    open={drawerOpen}
                    onClose={handleDrawerClose}
                />

            </div>

        </DashboardLayout>

    );

}

export default Teachers;