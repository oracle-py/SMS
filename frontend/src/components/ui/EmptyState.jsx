import "./EmptyState.css";
import Button from "./Button";

function EmptyState({

    icon,

    title = "Nothing Here",

    description = "There is currently no data to display.",

    actionLabel,

    onAction

}) {

    return (

        <div className="empty-state">

            <div className="empty-icon">

                {icon}

            </div>

            <h3>

                {title}

            </h3>

            <p>

                {description}

            </p>

            {actionLabel && (

                <Button

                    variant="primary"

                    onClick={onAction}

                >

                    {actionLabel}

                </Button>

            )}

        </div>

    );

}

export default EmptyState;