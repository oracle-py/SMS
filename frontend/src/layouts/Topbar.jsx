import { useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import {
    HiOutlineBars3,
    HiOutlineBell,
    HiOutlineMagnifyingGlass,
    HiOutlineCog6Tooth
} from "react-icons/hi2";

import "./Topbar.css";

const PAGE_INFO = {

    "/student/dashboard":{

        title:"Student Hub",

        subtitle:"Academic Overview"

    },

    "/student/results":{

        title:"Results",

        subtitle:"View your academic performance"

    },

    "/student/attendance":{

        title:"Attendance",

        subtitle:"Monitor your attendance records"

    },

    "/parent/dashboard":{

        title:"Dashboard",

        subtitle:"Ward Overview"

    },

    "/admin/dashboard":{

        title:"Dashboard",

        subtitle:"System Overview"

    },
    
    "/lecturer/dashboard":{

        title:"Dashboard",

        subtitle:"Lecturer Overview"

    },

    "/lecturer/courses":{

        title:"My Courses",

        subtitle:"Manage Assigned Courses"

    },

    "/lecturer/students":{

        title:"Students",

        subtitle:"Students Enrolled in Your Courses"

    },

    "/lecturer/results":{

        title:"Results",

        subtitle:"Upload and Manage Results"

    },

    "/lecturer/announcements":{

        title:"Announcements",

        subtitle:"Communicate with Students"

    },

    "/lecturer/profile":{

        title:"Profile",

        subtitle:"Account Information"

    }

};

export default function Topbar({

    toggleSidebar

}){

    const location=useLocation();

    const {user}=useAuth();

    const page=

        PAGE_INFO[location.pathname] ||

        {

            title:"SMS Portal",

            subtitle:"Smart Education Management"

        };

    const fullName=

        user?.first_name && user?.last_name

        ?

        `${user.first_name} ${user.last_name}`

        :

        user?.username ||

        "John Doe";

    const initials=

        fullName

        .split(" ")

        .map(name=>name[0])

        .join("")

        .substring(0,2)

        .toUpperCase();

    return(

        <header className="topbar">

            <div className="topbar-left">

                <button

                    className="menu-button"

                    onClick={toggleSidebar}

                >

                    <HiOutlineBars3/>

                </button>

                <div>

                    <h2>

                        {page.title}

                    </h2>

                    <p>

                        {page.subtitle}

                    </p>

                </div>

            </div>

            <div className="topbar-right">

                <div className="search-box">

                    <HiOutlineMagnifyingGlass/>

                    <input

                        type="text"

                        placeholder="Search..."

                    />

                </div>

                <button className="icon-button">

                    <HiOutlineBell/>

                    <span className="notification-dot"/>

                </button>

                <button className="icon-button">

                    <HiOutlineCog6Tooth/>

                </button>

                <div className="profile-chip">

                    <div className="profile-info">

                        <h4>

                            {fullName}

                        </h4>

                        <span>

                            {user?.role || "User"}

                        </span>

                    </div>

                    <div className="avatar">

                        {initials}

                    </div>

                </div>

            </div>

        </header>

    );

}