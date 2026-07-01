import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/axios";

import {
    FaUser,
    FaLock,
    FaEye,
    FaEyeSlash,
    FaGraduationCap,
    FaUsers,
    FaChalkboardTeacher,
    FaChartLine,
    FaCheckCircle,
    FaUserGraduate,
    FaUserShield,
    FaUserTie,
    FaArrowRight,
    FaUniversity,
    FaShieldAlt
} from "react-icons/fa";

import "./Login.css";

function Login() {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [remember, setRemember] = useState(false);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [stats, setStats] = useState({
        students: "Loading...",
        lecturers: "Loading...",
        trustScore: "Loading..."
    });

    const { login } = useAuth();

    const navigate = useNavigate();

    useEffect(() => {
        fetchLoginStats();
    }, []);

    const fetchLoginStats = async () => {
        try {
            const response = await api.get('/stats/public/');
            setStats({
                students: response.data.students || "0",
                lecturers: response.data.lecturers || "0",
                trustScore: response.data.trust_score || "95%"
            });
        } catch (error) {
            console.error('Error fetching login stats:', error);
            setStats({
                students: "2,400+",
                lecturers: "160+",
                trustScore: "95%"
            });
        }
    };

    const demoAccounts = [

        {
            role: "Administrator",
            username: "admin",
            password: "admin123",
            icon: FaUserShield
        },

        {
            role: "Student",
            username: "student1",
            password: "student123",
            icon: FaUserGraduate
        },

        {
            role: "Lecturer",
            username: "lecturer1",
            password: "lecturer123",
            icon: FaChalkboardTeacher
        },

        {
            role: "Parent",
            username: "parent1",
            password: "parent123",
            icon: FaUsers
        }

    ];

    const fillDemo = (username, pass) => {

        setEmail(username);
        setPassword(pass);

    };

    const handleSubmit = async (e) => {

        e.preventDefault();

        setError("");

        setLoading(true);

        const result = await login(email, password);

        if (result.success) {

            const role = JSON.parse(
                localStorage.getItem("user_data")
            )?.role;

            switch (role) {

                case "student":

                    navigate("/student/dashboard");
                    break;

                case "parent":

                    navigate("/parent/dashboard");
                    break;

                case "lecturer":

                    navigate("/lecturer/dashboard");
                    break;

                case "admin":

                    navigate("/admin/dashboard");
                    break;

                default:

                    navigate("/unauthorized");

            }

        } else {

            setError(result.error);

        }

        setLoading(false);

    };

    return (

        <div className="login-page">

            <div className="blob blob-one"></div>
            <div className="blob blob-two"></div>
            <div className="blob blob-three"></div>

            <div className="login-wrapper">

                {/* =========================
                    LEFT PANEL
                ========================= */}

                <div className="brand-panel">

                    <div>

                        <div className="brand-logo">

                            <FaUniversity />

                            <span>SMS Portal</span>

                        </div>

                        <h1>

                            Smart School

                            <span> Management System</span>

                        </h1>

                        <p>

                            A modern education platform connecting students,
                            lecturers, parents and administrators through one
                            intelligent academic ecosystem.

                        </p>

                    </div>

                    <div className="hero-illustration">

                        <svg
                            viewBox="0 0 700 420"
                            xmlns="http://www.w3.org/2000/svg"
                        >

                            <defs>

                                <linearGradient
                                    id="grad1"
                                    x1="0%"
                                    y1="0%"
                                    x2="100%"
                                    y2="100%"
                                >

                                    <stop
                                        offset="0%"
                                        stopColor="#7C83FF"
                                    />

                                    <stop
                                        offset="100%"
                                        stopColor="#4F46E5"
                                    />

                                </linearGradient>

                            </defs>

                            <circle
                                cx="350"
                                cy="200"
                                r="150"
                                fill="rgba(255,255,255,.05)"
                            />

                            <rect
                                x="170"
                                y="110"
                                rx="18"
                                ry="18"
                                width="360"
                                height="210"
                                fill="url(#grad1)"
                            />

                            <rect
                                x="205"
                                y="145"
                                width="290"
                                height="120"
                                rx="12"
                                fill="white"
                            />

                            <rect
                                x="230"
                                y="170"
                                width="90"
                                height="14"
                                rx="7"
                                fill="#CBD5E1"
                            />

                            <rect
                                x="230"
                                y="205"
                                width="220"
                                height="10"
                                rx="5"
                                fill="#E2E8F0"
                            />

                            <rect
                                x="230"
                                y="230"
                                width="180"
                                height="10"
                                rx="5"
                                fill="#E2E8F0"
                            />

                            <circle
                                cx="470"
                                cy="183"
                                r="18"
                                fill="#10B981"
                            />

                            <circle
                                cx="470"
                                cy="240"
                                r="18"
                                fill="#F59E0B"
                            />

                            <circle
                                cx="150"
                                cy="85"
                                r="20"
                                fill="#10B981"
                            />

                            <circle
                                cx="560"
                                cy="320"
                                r="26"
                                fill="#F59E0B"
                            />

                        </svg>

                    </div>

                    <div className="stats-grid">

                        <div className="stat-card">

                            <FaUsers />

                            <h2>{stats.students}</h2>

                            <p>Students</p>

                        </div>

                        <div className="stat-card">

                            <FaChalkboardTeacher />

                            <h2>{stats.lecturers}</h2>

                            <p>Lecturers</p>

                        </div>

                        <div className="stat-card">

                            <FaShieldAlt />

                            <h2>{stats.trustScore}</h2>

                            <p>Trust Score</p>

                        </div>

                    </div>

                    <div className="feature-list">

                        <div>

                            <FaCheckCircle />

                            <span>Attendance Monitoring</span>

                        </div>

                        <div>

                            <FaCheckCircle />

                            <span>Academic Performance Tracking</span>

                        </div>

                        <div>

                            <FaCheckCircle />

                            <span>Parent Communication Portal</span>

                        </div>

                        <div>

                            <FaCheckCircle />

                            <span>Administrative Analytics</span>

                        </div>

                    </div>

                </div>

                                {/* =========================
                    RIGHT PANEL
                ========================= */}

                <div className="login-section">

                    <div className="login-card">

                        <div className="login-header">

                            <div className="login-badge">

                                <FaGraduationCap />

                            </div>

                            <h2>

                                Welcome Back 👋

                            </h2>

                            <p>

                                Sign in to continue to your dashboard and manage
                                your academic activities.

                            </p>

                        </div>

                        <form onSubmit={handleSubmit}>

                            <div className="input-group">

                                <FaUser className="input-icon" />

                                <input

                                    type="text"

                                    placeholder="Username"

                                    value={email}

                                    onChange={(e)=>setEmail(e.target.value)}

                                    required

                                />

                            </div>

                            <div className="input-group">

                                <FaLock className="input-icon" />

                                <input

                                    type={showPassword ? "text" : "password"}

                                    placeholder="Password"

                                    value={password}

                                    onChange={(e)=>setPassword(e.target.value)}

                                    required

                                />

                                <button

                                    type="button"

                                    className="eye-btn"

                                    onClick={()=>setShowPassword(!showPassword)}

                                >

                                    {

                                        showPassword

                                        ?

                                        <FaEyeSlash/>

                                        :

                                        <FaEye/>

                                    }

                                </button>

                            </div>

                            <div className="login-options">

                                <label>

                                    <input

                                        type="checkbox"

                                        checked={remember}

                                        onChange={()=>setRemember(!remember)}

                                    />

                                    Remember Me

                                </label>

                                <a href="#">

                                    Forgot Password?

                                </a>

                            </div>

                            {

                                error &&

                                <div className="login-error">

                                    {error}

                                </div>

                            }

                            <button

                                type="submit"

                                className="login-btn"

                                disabled={loading}

                            >

                                {

                                    loading

                                    ?

                                    <>

                                        <span className="spinner"></span>

                                        Signing In...

                                    </>

                                    :

                                    <>

                                        Sign In

                                        <FaArrowRight/>

                                    </>

                                }

                            </button>

                        </form>

                        {/* ==========================
                            DEMO ACCOUNTS
                        =========================== */}

                        <div className="demo-box">

                            <div className="demo-header">

                                <h4>

                                    Demo Accounts

                                </h4>

                                <p>

                                    Click any account below to automatically
                                    fill the login form.

                                </p>

                            </div>

                            <div className="demo-grid">

                                {

                                    demoAccounts.map((account)=>{

                                        const Icon=account.icon;

                                        return(

                                            <button

                                                key={account.role}

                                                type="button"

                                                className="demo-card"

                                                onClick={()=>fillDemo(

                                                    account.username,

                                                    account.password

                                                )}

                                            >

                                                <div className="demo-icon">

                                                    <Icon/>

                                                </div>

                                                <div className="demo-details">

                                                    <h5>

                                                        {account.role}

                                                    </h5>

                                                    <span>

                                                        {account.username}

                                                    </span>

                                                </div>

                                            </button>

                                        );

                                    })

                                }

                            </div>

                        </div>

                        <div className="login-footer">

                            <span>

                                Smart School Management System

                            </span>

                            <small>

                                © 2026 All Rights Reserved

                            </small>

                        </div>

                    </div>

                </div>

            </div>

        </div>

    );

}

export default Login;