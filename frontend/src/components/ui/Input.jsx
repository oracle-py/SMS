import { forwardRef } from "react";
import "./Input.css";

const Input = forwardRef(({

    label,

    error,

    icon,

    rightIcon,

    fullWidth = true,

    className = "",

    ...props

}, ref) => {

    return (

        <div
            className={`input-group ${fullWidth ? "input-full" : ""}`}
        >

            {label && (

                <label className="input-label">

                    {label}

                </label>

            )}

            <div
                className={`
                    input-wrapper
                    ${error ? "input-error" : ""}
                `}
            >

                {icon && (

                    <span className="input-icon">

                        {icon}

                    </span>

                )}

                <input

                    ref={ref}

                    className={`
                        ui-input
                        ${icon ? "has-left-icon" : ""}
                        ${rightIcon ? "has-right-icon" : ""}
                        ${className}
                    `}

                    {...props}

                />

                {rightIcon && (

                    <span className="input-right-icon">

                        {rightIcon}

                    </span>

                )}

            </div>

            {error && (

                <p className="input-error-text">

                    {error}

                </p>

            )}

        </div>

    );

});

export default Input;