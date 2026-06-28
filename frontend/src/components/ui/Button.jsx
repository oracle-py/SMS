import "./Button.css";

function Button({
    children,
    variant = "primary",
    size = "md",
    fullWidth = false,
    loading = false,
    disabled = false,
    icon = null,
    type = "button",
    onClick
}) {

    return (

        <button
            type={type}
            className={`
                btn
                btn-${variant}
                btn-${size}
                ${fullWidth ? "btn-full" : ""}
                ${loading ? "btn-loading" : ""}
            `}
            disabled={disabled || loading}
            onClick={onClick}
        >

            {loading && (
                <span className="btn-spinner"></span>
            )}

            {!loading && icon && (
                <span className="btn-icon">
                    {icon}
                </span>
            )}

            <span className="btn-text">
                {loading ? "Please wait..." : children}
            </span>

        </button>

    );

}

export default Button;