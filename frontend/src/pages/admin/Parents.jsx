import { useState, useEffect } from "react";
import {
    HiOutlineTrash,
    HiOutlineUserGroup
} from "react-icons/hi2";

import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import { useDashboardRefresh } from "../../context/DashboardContext";

import "./admin.css";

function Parents() {

    const { refreshDashboard } = useDashboardRefresh();

    const [parents, setParents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchParents();
    }, []);

    async function fetchParents() {

        setLoading(true);

        try {

            const response = await api.get("/parents/");
            setParents(response.data.results || response.data);

        } catch (error) {

            console.error(error);

        } finally {

            setLoading(false);

        }
    }

    const handleDelete = async (parentId) => {
        if (!window.confirm('Are you sure you want to delete this parent?')) {
            return;
        }
        try {
            await api.delete(`/parents/${parentId}/`);
            fetchParents();
            refreshDashboard();
        } catch (error) {
            console.error('Error deleting parent:', error);
            alert('Failed to delete parent');
        }
    };

    return (

        <DashboardLayout>

            <div className="ad-page">

                <div className="students-header-box">

                    <div className="students-header-content">

                        <div className="students-header-icon">

                            <HiOutlineUserGroup />

                        </div>

                        <div className="students-header-text">

                            <h1>
                                Parents
                            </h1>

                            <p>
                                Manage parents and guardians linked to registered students.
                            </p>

                        </div>

                    </div>

                </div>

                <div className="ad-stat-strip">

                    <div>

                        <span>Total Parents</span>

                        <h2>{parents.length}</h2>

                    </div>

                </div>

                {

                    loading ?

                        <div className="ad-loading">

                            Loading parents...

                        </div>

                        :

                        <div className="ad-card">

                            <table className="ad-table">

                                <thead>

                                    <tr>

                                        <th>Parent</th>
                                        <th>Email</th>
                                        <th>Phone</th>
                                        <th>Occupation</th>
                                        <th>Children</th>
                                        <th></th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {

                                        parents.length > 0 ?

                                            parents.map((parent) => {

                                                const fullName =
                                                    `${parent.user?.first_name || ""} ${parent.user?.last_name || ""}`;

                                                const initials = fullName
                                                    .trim()
                                                    .split(" ")
                                                    .map((n) => n[0])
                                                    .join("")
                                                    .substring(0, 2)
                                                    .toUpperCase();

                                                return (

                                                    <tr key={parent.id}>

                                                        <td>

                                                            <div className="ad-student">

                                                                <div className="ad-avatar">

                                                                    {initials}

                                                                </div>

                                                                <div>

                                                                    <h4>

                                                                        {fullName}

                                                                    </h4>

                                                                    <span>

                                                                        Parent / Guardian

                                                                    </span>

                                                                </div>

                                                            </div>

                                                        </td>

                                                        <td>

                                                            {parent.user?.email}

                                                        </td>

                                                        <td>

                                                            {parent.user?.phone || "—"}

                                                        </td>

                                                        <td>

                                                            {parent.occupation || "—"}

                                                        </td>

                                                        <td>

                                                            {parent.children_count || 0}

                                                        </td>

                                                        <td>

                                                            <div className="ad-action-buttons">

                                                                <button onClick={() => handleDelete(parent.id)}>

                                                                    <HiOutlineTrash />

                                                                </button>

                                                            </div>

                                                        </td>

                                                    </tr>

                                                );

                                            })

                                            :

                                            <tr>

                                                <td
                                                    colSpan="6"
                                                    className="ad-empty-state"
                                                >

                                                    No parents found.

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

export default Parents;