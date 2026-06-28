import "./StatCard.css";

function StatCard({

    title,

    value,

    subtitle,

    icon,

    color = "primary",

    trend,

    trendLabel,

    onClick

}){

    return(

        <div

            className="stat-card"

            onClick={onClick}

        >

            <div className="stat-top">

                <div className={`stat-icon ${color}`}>

                    {icon}

                </div>

                {trend && (

                    <div
                        className={`
                            stat-trend
                            ${trend > 0 ? "positive" : "negative"}
                        `}
                    >

                        {trend > 0 ? "▲" : "▼"}

                        {Math.abs(trend)}%

                    </div>

                )}

            </div>

            <div className="stat-content">

                <span className="stat-title">

                    {title}

                </span>

                <h2>

                    {value}

                </h2>

                {subtitle && (

                    <p>

                        {subtitle}

                    </p>

                )}

                {trendLabel && (

                    <small>

                        {trendLabel}

                    </small>

                )}

            </div>

        </div>

    );

}

export default StatCard;