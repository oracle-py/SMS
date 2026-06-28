import { useAuth } from "../../context/AuthContext";
import DashboardLayout from "../../layouts/DashboardLayout";
import './Lecturer.css';

export default function Profile() {

    const { user } = useAuth();

    return (

        <DashboardLayout userRole="lecturer">

            <div className="lecturer-page">

                <div className="lecturer-header">
                    <h1>Profile</h1>
                </div>

                <div className="lecturer-card">

                    <p><strong>Name:</strong> {user?.first_name} {user?.last_name}</p>

                    <p><strong>Email:</strong> {user?.email}</p>

                    <p><strong>Role:</strong> Lecturer</p>

                </div>

            </div>

        </DashboardLayout>

    );

}