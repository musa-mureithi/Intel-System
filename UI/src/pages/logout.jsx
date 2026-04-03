import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

const BASE_URL = "http://127.0.0.1:8000";

function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
     console.log("🔥 Logout page loaded");
    const handleLogout = async () => {
         console.log("🔥 Running logout...");
        
      try {
        const access = localStorage.getItem("access_token");
        const refresh = localStorage.getItem("refresh_token");
        if (refresh) {
          await fetch(`${BASE_URL}/logout/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${access}`,
            },
            body: JSON.stringify({ refresh }),
          });
        }
      } catch (err) {
        console.warn("Logout error:", err);
      } finally {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("profile");
        navigate("/login");
      }
    };

    handleLogout();
  }, [navigate]);

  return (
    <div className="logout-page">
      <h2>Logging out...</h2>
      <p>Please wait</p>
    </div>
  );
}

export default Logout;