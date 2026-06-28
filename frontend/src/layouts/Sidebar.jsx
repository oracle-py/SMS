import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import { navigation, BRAND } from "./navigation";

import { HiChevronLeft, HiChevronRight } from "react-icons/hi";
import { HiOutlineLogout } from "react-icons/hi";

import "./Sidebar.css";

function Sidebar({

    isOpen,

    toggleSidebar

}){

    const navigate = useNavigate();

    const location = useLocation();

    const { user, logout } = useAuth();

    const role = user?.role || "student";

    const menu = navigation[role] || [];

    const Logo = BRAND.logo;

    const fullName =

        user?.first_name && user?.last_name

            ? `${user.first_name} ${user.last_name}`

            : user?.username || "John Doe";

    const roleLabel = {

        student:"Student",

        parent:"Parent",

        admin:"Administrator",

        lecturer:"Lecturer"

    };

    async function handleLogout(){

        await logout();

        navigate("/");

    }

    return(

        <aside

            className={`sidebar ${isOpen ? "open" : "closed"}`}

        >

            {/* Brand */}

            <div className="sidebar-brand">

                <div className="brand-logo">

                    <Logo/>

                </div>

                {

                    isOpen &&

                    <div className="brand-text">

                        <h2>

                            {BRAND.name}

                        </h2>

                        <p>

                            {BRAND.subtitle}

                        </p>

                    </div>

                }

                <button

                    className="collapse-button"

                    onClick={toggleSidebar}

                >

                    {

                        isOpen

                        ?

                        <HiChevronLeft/>

                        :

                        <HiChevronRight/>

                    }

                </button>

            </div>

            {/* Navigation */}

            <div className="sidebar-menu">

                {

                    menu.map(section=>(

                        <div

                            key={section.section}

                            className="sidebar-section"

                        >

                            {

                                isOpen &&

                                <span className="section-title">

                                    {section.section}

                                </span>

                            }

                            {

                                section.items.map(item=>{

                                    const Icon=item.icon;

                                    const active=

                                        location.pathname===item.path;

                                    return(

                                        <button

                                            key={item.path}

                                            className={`nav-item ${active?"active":""}`}

                                            onClick={()=>navigate(item.path)}

                                        >

                                            <div className="nav-icon">

                                                <Icon/>

                                            </div>

                                            {

                                                isOpen &&

                                                <span>

                                                    {item.label}

                                                </span>

                                            }

                                        </button>

                                    );

                                })

                            }

                        </div>

                    ))

                }

            </div>

            {/* Footer */}

            <div className="sidebar-footer">

                {

                    isOpen &&

                    <div className="user-card">

                        <div className="online-dot"/>

                        <div>

                            <h4>

                                {fullName}

                            </h4>

                            <p>

                                {roleLabel[role]}

                            </p>

                        </div>

                    </div>

                }

                <button

                    className="logout-button"

                    onClick={handleLogout}

                >

                    <HiOutlineLogout/>

                    {

                        isOpen &&

                        <span>

                            Sign Out

                        </span>

                    }

                </button>

            </div>

        </aside>

    );

}

export default Sidebar;