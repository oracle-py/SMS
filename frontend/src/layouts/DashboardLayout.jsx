import { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import "./DashboardLayout.css";

export default function DashboardLayout({ children }) {

    const [sidebarOpen, setSidebarOpen] = useState(() => {
        const saved = localStorage.getItem("sidebarOpen");
        if (saved !== null) return saved === "true";
        return true;
    });

    useEffect(() => {

        localStorage.setItem("sidebarOpen", sidebarOpen);

    }, [sidebarOpen]);

    useEffect(() => {

        const handleResize = () => {

            if (window.innerWidth <= 900) {

                setSidebarOpen(false);

            }

        };

        window.addEventListener("resize", handleResize);

        return () => window.removeEventListener("resize", handleResize);

    }, []);

    return (

        <div className="dashboard-layout">

            <Sidebar

                isOpen={sidebarOpen}

                toggleSidebar={() => setSidebarOpen(!sidebarOpen)}

            />

            {/* Mobile Overlay */}

            {sidebarOpen && window.innerWidth <= 900 && (

                <div

                    className="sidebar-overlay"

                    onClick={() => setSidebarOpen(false)}

                />

            )}

            <div

                className={`dashboard-main ${
                    sidebarOpen ? "sidebar-open" : "sidebar-closed"
                }`}

            >

                <Topbar

                    toggleSidebar={() => setSidebarOpen(!sidebarOpen)}

                />

                <main className="dashboard-content">

                    {children}

                </main>

            </div>

        </div>

    );

}