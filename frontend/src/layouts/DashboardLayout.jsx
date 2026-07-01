import { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import "./DashboardLayout.css";

export default function DashboardLayout({ children }) {

    const [sidebarOpen, setSidebarOpen] = useState(() => {
        const saved = localStorage.getItem("sidebarOpen");
        if (saved !== null) return saved === "true";
        return false; // Start closed by default for all accounts
    });

    useEffect(() => {

        localStorage.setItem("sidebarOpen", sidebarOpen);

    }, [sidebarOpen]);

    useEffect(() => {

        const handleResize = () => {

            if (window.innerWidth <= 900) {

                setSidebarOpen(false);

            }
            // Don't auto-open on desktop - respect user preference

        };

        window.addEventListener("resize", handleResize);

        return () => window.removeEventListener("resize", handleResize);

    }, []);

    // Scroll to top on mount
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    return (

        <div className="dashboard-layout">

            <Sidebar

                isOpen={sidebarOpen}

                toggleSidebar={toggleSidebar}

            />

            {/* Mobile Overlay */}

            <div
                className={`sidebar-overlay ${sidebarOpen ? 'active' : ''}`}
                onClick={toggleSidebar}
            />

            <div
                className={`dashboard-main ${
                    sidebarOpen ? "sidebar-open" : "sidebar-closed"
                }`}
            >

                <Topbar
                    toggleSidebar={toggleSidebar}
                />

                <main className="dashboard-content">

                    {children}

                </main>

            </div>

        </div>

    );

}