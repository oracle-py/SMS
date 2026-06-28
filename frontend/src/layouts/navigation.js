import {
    LuLayoutDashboard,
    LuClipboardList,
    LuCalendarCheck,
    LuUsers,
    LuSchool,
    LuBookOpen,
    LuTrendingUp,
    LuSettings,
    LuGraduationCap,
    LuCalendar
} from "react-icons/lu";

import { PiStudentBold } from "react-icons/pi";

import { FaChalkboardUser } from "react-icons/fa6";

import { MdFamilyRestroom } from "react-icons/md";

export const navigation = {

    student: [

        {
            section: "MAIN",

            items: [

                {
                    label: "Dashboard",
                    path: "/student/dashboard",
                    icon: LuLayoutDashboard
                },

                {
                    label: "Results",
                    path: "/student/results",
                    icon: LuClipboardList
                },

                {
                    label: "Attendance",
                    path: "/student/attendance",
                    icon: LuCalendarCheck
                },

                {
                    label: "Courses",
                    path: "/student/courses",
                    icon: LuBookOpen
                },

                {
                    label: "Lecturers",
                    path: "/student/lecturers",
                    icon: FaChalkboardUser
                },

                {
                    label: "Timetable",
                    path: "/student/timetable",
                    icon: LuCalendar
                }

            ]

        }

    ],

    parent: [

        {

            section: "MAIN",

            items: [

                {

                    label: "Dashboard",

                    path: "/parent/dashboard",

                    icon: LuLayoutDashboard

                },

                {

                    label: "Children",

                    path: "/parent/wards",

                    icon: PiStudentBold

                },

                {

                    label: "Results",

                    path: "/parent/results",

                    icon: LuClipboardList

                },

                {

                    label: "Attendance",

                    path: "/parent/attendance",

                    icon: LuCalendarCheck

                }

            ]

        }

    ],

    admin: [

        {

            section: "MAIN",

            items: [

                {

                    label: "Dashboard",

                    path: "/admin/dashboard",

                    icon: LuLayoutDashboard

                }

            ]

        },

        {

            section: "MANAGEMENT",

            items: [

                {

                    label: "Students",

                    path: "/admin/students",

                    icon: PiStudentBold

                },

                {

                    label: "Teachers",

                    path: "/admin/teachers",

                    icon: FaChalkboardUser

                },

                {

                    label: "Parents",

                    path: "/admin/parents",

                    icon: MdFamilyRestroom

                },

                {

                    label: "Classes",

                    path: "/admin/classes",

                    icon: LuSchool

                },

                {

                    label: "Subjects",

                    path: "/admin/subjects",

                    icon: LuBookOpen

                },

                {

                    label: "Results",

                    path: "/admin/results",

                    icon: LuClipboardList

                },

                {

                    label: "Attendance",

                    path: "/admin/attendance",

                    icon: LuCalendarCheck

                }

            ]

        },

        {

            section: "SYSTEM",

            items: [

                {

                    label: "Analytics",

                    path: "/admin/analytics",

                    icon: LuTrendingUp

                },

                {

                    label: "Settings",

                    path: "/admin/settings",

                    icon: LuSettings

                }

            ]

        }

    ],
    lecturer: [

        {

            section: "MAIN",

            items: [

                {

                    label: "Dashboard",

                    path: "/lecturer/dashboard",

                    icon: LuLayoutDashboard

                }

            ]

        },

        {

            section: "ACADEMICS",

            items: [

                {

                    label: "My Courses",

                    path: "/lecturer/courses",

                    icon: LuBookOpen

                },

                {

                    label: "Students",

                    path: "/lecturer/students",

                    icon: LuUsers

                },

                {

                    label: "Results",

                    path: "/lecturer/results",

                    icon: LuClipboardList

                }

            ]

        },

        {

            section: "COMMUNICATION",

            items: [

                {

                    label: "Announcements",

                    path: "/lecturer/announcements",

                    icon: LuCalendar

                }

            ]

        },

        {

            section: "ACCOUNT",

            items: [

                {

                    label: "Profile",

                    path: "/lecturer/profile",

                    icon: LuSettings

                }

            ]

        }

    ]

};

export const BRAND = {

    name: "SMS Portal",

    subtitle: "Smart Education Management",

    logo: LuGraduationCap

};
