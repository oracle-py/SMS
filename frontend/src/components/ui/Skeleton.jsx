import "./Skeleton.css";

function Skeleton({

    width = "100%",

    height = 16,

    radius = 10,

    className = ""

}) {

    return (

        <div

            className={`skeleton ${className}`}

            style={{

                width,

                height,

                borderRadius: radius

            }}

        />

    );

}

export default Skeleton;