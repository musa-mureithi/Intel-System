import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "../App.css";
import useSearch from "../hook/useSearch"; 
/*import Operation from "./operation";*/


const BASE_URL = "https://75lsvb8q-8000.inc1.devtunnels.ms";

const Dashboard = () => {
  const [profile, setProfile] = useState(null);
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const { results, loading: searchLoading, error: searchError, search } = useSearch();
  

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem("access_token");
      if (!token) return (window.location.href = "/login");

      const res = await fetch(`${BASE_URL}/dashboard/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error("Failed to fetch dashboard");

      const data = await res.json();
      setProfile(data.profile || null);
      setOperations(data.operations || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    search(searchQuery);
  };
  if (loading)
    return (
      <div className="dashboard center">
        <div className="loader">SCANNING DATABASE...</div>
      </div>
    );
  if (error)
    return (
      <div className="dashboard center">
        <div className="error">{error}</div>
        <button onClick={fetchDashboard}>RETRY</button>
      </div>
    );

  return (
    <div className="dashboard">
      {/* TOP BAR */}
      <div className="topbar">
        <span>INTELLIGENT SYSTEM</span>
        <span className="title">CLASSIFIED DATABASE</span>
      </div>

      <div className="main">
        {/* SIDEBAR */}
        <div className="sidebar">
          <h3 style={{ color: "white" }}>CONTROL PANEL</h3>
          <ul>
            <li><button><Link to="/logout">Logout</Link></button></li>
            <li><Link to="/Audit-logs">Audit Logs</Link></li>
            <li> <Link to="/operation">Operation</Link></li>
             <li><Link to="/report">Report</Link></li>
            <li> <Link to="/scan">Search</Link></li>
             <li>Personnel</li>
          </ul>
        </div>

        {/* CONTENT */}
        <div className="content">
          {/* LEFT PANEL: SEARCH + OPERATIONS */}
          <div className="left-panel">
            {/* SEARCH */}
            <div className="panel">
              <div className="panel-header">{'simple search'.toUpperCase()}</div>
              <div className="filters">
                <input
                  placeholder="Search by Name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <button onClick={handleSearch}>SEARCH</button>
              </div>

              <div className="list">
                {searchLoading && <p className="text-muted">Searching...</p>}
                {searchError && <p className="text-muted error">{searchError}</p>}

                {results.length === 0 ? (
                  <p className="text-muted">No results found</p>
                ) : (
                  results.map((p) => (
                    <div key={p.id} className="list-item">
                      <div className="person-info">
                        <p><strong>{p.full_name || "Unknown"}</strong></p>
                        <p>Identity: {p.identity_number || "REDACTED"}</p>
                        <p>Type: {p.person_type || "REDACTED"}</p>
                        <p>Unit: {p.unit_type || "REDACTED"}</p>
                        <p>Blood: {p.blood_type || "REDACTED"}</p>
                        
                        <span className="text-muted">
                          Clearance: {p.clearance_type || "REDACTED"}
                        </span>
                      </div>
                      <span className="dot green"></span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* OPERATIONS */}
            <div className="panel">
              <div className="panel-header">ACTIVE OPERATIONS</div>
              {operations.length === 0 ? (
                <p className="text-muted">No active operations</p>
              ) : (
                operations.map((op, i) => (
                  <div key={i} className="operation-card">
                    <div className="op-title">{op.codename || "UNKNOWN"}</div>
                    <div className="op-desc">{op.description || "No details"}</div>
                    <span className="classified-tag">CLASSIFIED</span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* RIGHT PANEL: PROFILE */}
          <div className="right-panel">
            <div className="panel">
              <div className="panel-header">PERSONNEL PROFILE</div>
              {!profile ? (
                <p className="text-muted">No profile loaded</p>
              ) : (
                <>
                 <p className="profile-img">Image: {profile.image ? <img src={profile.image} alt="" width="150" /> : "No image available"}</p>
                  <div className="profile-info">
                    <p>
                      <strong>{profile.full_name}</strong> ({profile.person_type})
                    </p>
                    <p>Unit: {profile.unit_type || "N/A"}</p>
                    <p>Blood: {profile.blood_type || "N/A"}</p>
                    <p>DNA ID: {profile.id_dna || "N/A"}</p>
                    <p>Identity Number: {profile.identity_number || "N/A"}</p>
                   {/* <p>OPs: {profile.Operation|| "N/A"}</p>*/}
                    <p>
                      Clearance:{" "}
                      <span className="classified">{profile.clearance_type || "N/A"}</span>
                    </p>
                    <p>TOTP Secret: {profile.totp_secret || "N/A"}</p>
                    <p>
                      Face Embeddings:{" "}
                      {profile.face_embeddings
                        ? `[${profile.face_embeddings.slice(0, 5)} ...]`
                        : "N/A"}
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;