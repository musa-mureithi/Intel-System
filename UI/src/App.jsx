import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Dashboard from "./pages/dashboard";
import Operation from "./pages/operation";
import Report from "./pages/report";
import Logout from "./pages/logout";
import Scan from "./pages/scan";
import AuditLogs from "./pages/auditLogs";
import ErrorBoundary from "./pages/ErrorBoundary";
import {jwtDecode} from "jwt-decode";
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    return <Navigate to="/login" />;
  }
 /* if (!user) return <Navigate to="/login" />;
  if (!user.is_staff) return <Navigate to="/" />; */
  try {
    const decoded = jwtDecode(token);
    const isExpired = decoded.exp * 1000 < Date.now();

    if (isExpired) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      return <Navigate to="/login" />;
    }

  } catch (err) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    return <Navigate to="/login" />;
  }
  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<PrivateRoute><ErrorBoundary><Dashboard /> </ErrorBoundary></PrivateRoute>}/>
        <Route path="/operation" element={<PrivateRoute><Operation /></PrivateRoute>} />
         <Route path="/report" element={<PrivateRoute><Report /></PrivateRoute>} />
          <Route path="/logout" element={<PrivateRoute><Logout /></PrivateRoute>} />
          <Route path="/scan" element={<PrivateRoute><Scan /></PrivateRoute>} />
          <Route path="/audit-logs" element={<PrivateRoute><AuditLogs /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;