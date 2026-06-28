import DashboardLayout from "../../layouts/DashboardLayout";
import './Lecturer.css';

const courses = [
    {
        code: "CSC401",
        title: "Database Systems",
        level: "400"
    },
    {
        code: "CSC402",
        title: "Artificial Intelligence",
        level: "400"
    },
    {
        code: "MEE302",
        title: "Thermodynamics",
        level: "300"
    }
];

export default function Courses() {

    return (

        <DashboardLayout userRole="lecturer">

            <div className="lecturer-page">

                <div className="lecturer-header">
                    <h1>My Courses</h1>
                </div>

                <div className="lecturer-card">

                    <table className="lecturer-table">

                        <thead>

                            <tr>
                                <th>Code</th>
                                <th>Course</th>
                                <th>Level</th>
                                <th></th>
                            </tr>

                        </thead>

                        <tbody>

                            {courses.map(course => (

                                <tr key={course.code}>
                                    <td>{course.code}</td>
                                    <td>{course.title}</td>
                                    <td>{course.level}</td>

                                    <td>
                                        <button className="lecturer-btn">
                                            View Students
                                        </button>
                                    </td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            </div>

        </DashboardLayout>

    );

}