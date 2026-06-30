import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import Login from '../pages/Login';
import StudentDashboard from '../pages/student/StudentDashboard';
import StudentResults from '../pages/student/StudentResults';
import StudentAttendance from '../pages/student/StudentAttendance';
import StudentCourses from '../pages/student/StudentCourses';
import StudentLecturers from '../pages/student/StudentLecturers';
import StudentTimetable from '../pages/student/StudentTimetable';
import ParentDashboard from '../pages/ParentDashboard';
import LecturerDashboard from '../pages/lecturer/LecturerDashboard';
import LecturerCourses from '../pages/lecturer/Courses';
import LecturerStudents from '../pages/lecturer/Students';
import LecturerResults from '../pages/lecturer/Results';
import LecturerAnnouncements from '../pages/lecturer/Announcements';
import LecturerProfile from '../pages/lecturer/Profile';
import AdminDashboard from '../pages/admin/AdminDashboard';
import Students from '../pages/admin/Students';
import Teachers from '../pages/admin/Teachers';
import Parents from '../pages/admin/Parents';
import Courses from '../pages/admin/Courses';
import UnderDevelopment from '../pages/UnderDevelopment';
import Unauthorized from '../pages/Unauthorized';
import ProtectedRoute from '../components/ProtectedRoute';

function AppRoutes() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
        <Route 
          path="/student/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentDashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/student/results" 
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentResults />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/student/attendance" 
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentAttendance />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/student/courses" 
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentCourses />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/student/lecturers" 
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentLecturers />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/student/timetable" 
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentTimetable />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/parent/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['parent']}>
              <ParentDashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/parent/wards" 
          element={
            <ProtectedRoute allowedRoles={['parent']}>
              <UnderDevelopment feature="Children Management" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/parent/results" 
          element={
            <ProtectedRoute allowedRoles={['parent']}>
              <UnderDevelopment feature="Results Management" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/parent/attendance" 
          element={
            <ProtectedRoute allowedRoles={['parent']}>
              <UnderDevelopment feature="Attendance Management" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/lecturer/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['lecturer']}>
              <LecturerDashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/lecturer/courses" 
          element={
            <ProtectedRoute allowedRoles={['lecturer']}>
              <LecturerCourses />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/lecturer/students" 
          element={
            <ProtectedRoute allowedRoles={['lecturer']}>
              <LecturerStudents />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/lecturer/results" 
          element={
            <ProtectedRoute allowedRoles={['lecturer']}>
              <LecturerResults />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/lecturer/announcements" 
          element={
            <ProtectedRoute allowedRoles={['lecturer']}>
              <LecturerAnnouncements />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/lecturer/profile" 
          element={
            <ProtectedRoute allowedRoles={['lecturer']}>
              <LecturerProfile />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/students" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Students />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/teachers" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Teachers />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/parents" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Parents />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/classes" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Courses />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/subjects" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <UnderDevelopment feature="Courses Management" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/results" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <UnderDevelopment feature="Results Management" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/attendance" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <UnderDevelopment feature="Attendance Management" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/analytics" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <UnderDevelopment feature="Analytics Dashboard" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/settings" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <UnderDevelopment feature="Settings" />
            </ProtectedRoute>
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default AppRoutes;
