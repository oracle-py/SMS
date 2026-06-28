import "./Table.css";
import EmptyState from "./EmptyState";
import Skeleton from "./Skeleton";
import { FiInbox } from "react-icons/fi";

function Table({

    columns = [],

    data = [],

    loading = false,

    emptyTitle = "No Records Found",

    emptyDescription = "There are currently no records to display.",

    renderRow

}) {

    if (loading) {

        return (

            <div className="table-container">

                <table className="ui-table">

                    <thead>

                        <tr>

                            {columns.map((column) => (

                                <th key={column}>

                                    {column}

                                </th>

                            ))}

                        </tr>

                    </thead>

                    <tbody>

                        {[...Array(6)].map((_, index) => (

                            <tr key={index}>

                                {columns.map((column) => (

                                    <td key={column}>

                                        <Skeleton height={18} />

                                    </td>

                                ))}

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        );

    }

    if (!loading && data.length === 0) {

        return (

            <EmptyState

                icon={<FiInbox />}

                title={emptyTitle}

                description={emptyDescription}

            />

        );

    }

    return (

        <div className="table-container">

            <table className="ui-table">

                <thead>

                    <tr>

                        {columns.map((column) => (

                            <th key={column}>

                                {column}

                            </th>

                        ))}

                    </tr>

                </thead>

                <tbody>

                    {data.map((item, index) =>

                        renderRow(item, index)

                    )}

                </tbody>

            </table>

        </div>

    );

}

export default Table;