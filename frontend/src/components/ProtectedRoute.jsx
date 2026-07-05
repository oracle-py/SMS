import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading, authenticated } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user || !authenticated) {
    return <Navigate to="/" replace />;
  }

  // Only redirect to unauthorized if the user explicitly navigated to a route
  // they don't have permission for. Don't redirect on page refresh.
  // We detect this by checking if the user was previously authenticated
  // and had this role (stored in localStorage during login)
  const previousRole = localStorage.getItem('user_role');
  
  if (!allowedRoles.includes(user.role)) {
    // If the user's current role doesn't match, but they previously had a matching role,
    // this might be a refresh - allow them to stay
    if (previousRole && allowedRoles.includes(previousRole)) {
      return children;
    }
    // Otherwise, they're trying to access a route they shouldn't
    return <Navigate to="/unauthorized" replace />;
  }

  // Update the stored role to current role
  localStorage.setItem('user_role', user.role);

  return children;
};

export default ProtectedRoute;
