import DashboardLayout from "../../layouts/DashboardLayout";
import './Lecturer.css';

const students = [

    {
        id: 1,
        name: "John Musa"
    },

    {
        id: 2,
        name: "Mary James"
    }

];

export default function Results() {

    return (

        <DashboardLayout userRole="lecturer">

            <div className="lecturer-page">

                <div className="lecturer-header">
                    <h1>Results</h1>
                </div>

                <div className="lecturer-card">

                    <table className="lecturer-table">

                        <thead>

                            <tr>
                                <th>Student</th>
                                <th>CA</th>
                                <th>Exam</th>
                                <th>Total</th>
                                <th>Grade</th>
                            </tr>

                        </thead>

                        <tbody>

                            {students.map(student => (

                                <tr key={student.id}>

                                    <td>{student.name}</td>

                                    <td>
                                        <input className="lecturer-input" />
                                    </td>

                                    <td>
                                        <input className="lecturer-input" />
                                    </td>

                                    <td>-</td>

                                    <td>-</td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                    <button className="lecturer-btn">
                        Save Results
                    </button>

                </div>

            </div>

        </DashboardLayout>

    );

}