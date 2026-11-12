import { Navigate, Outlet, useLocation } from "react-router-dom";
import { dashboardPath, useAuth } from "../AuthContext";

// Frontend guard for convenience. The REAL security check happens on the backend for every API call.
export default function ProtectedRoute({ roles }) {
  const { user } = useAuth();
  const location = useLocation();
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  if (!roles.includes(user.role)) return <Navigate to={dashboardPath(user.role)} replace />;
  return <Outlet />;
}
