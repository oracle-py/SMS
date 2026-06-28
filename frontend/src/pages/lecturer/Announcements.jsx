import DashboardLayout from "../../layouts/DashboardLayout";
import './Lecturer.css';

export default function Announcements() {

    return (

        <DashboardLayout userRole="lecturer">

            <div className="lecturer-page">

                <div className="lecturer-header">
                    <h1>Announcements</h1>
                </div>

                <div className="lecturer-card">

                    <input
                        className="lecturer-input"
                        placeholder="Title"
                    />

                    <textarea
                        className="lecturer-textarea"
                        rows="5"
                        placeholder="Write Announcement..."
                    />

                    <button className="lecturer-btn">
                        Publish
                    </button>

                </div>

            </div>

        </DashboardLayout>

    );

}