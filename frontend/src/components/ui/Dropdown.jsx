import { useState } from "react";
import "./Dropdown.css";

function Dropdown({

    value,

    options=[],

    placeholder="Select..."

}){

    const[open,setOpen]=useState(false);

    return(

        <div className="dropdown">

            <button

                className="dropdown-trigger"

                onClick={()=>setOpen(!open)}

            >

                {value || placeholder}

            </button>

            {

                open &&

                <div className="dropdown-menu">

                    {

                        options.map(option=>

                            <button

                                key={option.value}

                                className="dropdown-item"

                                onClick={()=>{

                                    option.onClick();

                                    setOpen(false);

                                }}

                            >

                                {option.label}

                            </button>

                        )

                    }

                </div>

            }

        </div>

    );

}

export default Dropdown;