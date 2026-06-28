import DashboardLayout from "../../layouts/DashboardLayout";
import './Lecturer.css';

const students = [

    {
        name: "John Musa",
        matric: "UJ/FNS/20/001"
    },

    {
        name: "Mary James",
        matric: "UJ/FNS/20/005"
    },

    {
        name: "David Peter",
        matric: "UJ/FNS/20/012"
    }

];

export default function Students() {

    return (

        <DashboardLayout userRole="lecturer">

            <div className="lecturer-page">

                <div className="lecturer-header">
                    <h1>Students</h1>
                </div>

                <div className="lecturer-card">

                    <input
                        className="lecturer-input"
                        placeholder="Search Student..."
                    />

                    <table className="lecturer-table">

                        <thead>

                            <tr>
                                <th>Name</th>
                                <th>Matric Number</th>
                            </tr>

                        </thead>

                        <tbody>

                            {students.map(student => (

                                <tr key={student.matric}>
                                    <td>{student.name}</td>
                                    <td>{student.matric}</td>
                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            </div>

        </DashboardLayout>

    );

}