import React, { useEffect, useState } from "react";
import "../App.css";

const BASE_URL = "http://127.0.0.1:8000";

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchLogs = async (pageNumber = 1) => {
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("You are not logged in.");

      const response = await fetch(
        `${BASE_URL}/api/audit/get_logs?page=${pageNumber}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const contentType = response.headers.get("content-type");

      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("Session expired or unauthorized.");
      }

      if (response.status === 403) {
        throw new Error("Access denied. Superuser only.");
      }

      if (!response.ok) {
        throw new Error("Failed to fetch logs.");
      }

      const data = await response.json();
      setLogs(data.results);
      setPage(data.page);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(err.message);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs(page);
  }, [page]);

  const getActionClass = (action) => {
    switch (action?.toLowerCase()) {
      case "create":
        return "action-create";
      case "update":
        return "action-update";
      case "delete":
        return "action-delete";
      default:
        return "action-default";
    }
  };

  return (
    <div className="audit-container">
      <h2 className="audit-title">Audit Logs</h2>

      {error && <div className="audit-error">{error}</div>}
      {loading && <p>Loading logs...</p>}

      {!loading && (
        <div className="audit-table-wrapper">
          <table className="audit-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Action</th>
                <th>Resource</th>
                <th>IP</th>
                <th>Time</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {logs.length > 0 ? (
                logs.map((log) => (
                  <tr key={log.id}>
                    <td>{log.user}</td>
                    <td className={getActionClass(log.action)}>{log.action}</td>
                    <td>{log.resource}</td>
                    <td>{log.ip}</td>
                    <td>{new Date(log.time).toLocaleString()}</td>
                    <td>{log.description}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="audit-empty">
                    No logs found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="audit-pagination">
        <button onClick={() => setPage((p) => p - 1)} disabled={page <= 1 || loading}>
          ⬅ Prev
        </button>
        <span>
          Page {page} of {totalPages}
        </span>
        <button onClick={() => setPage((p) => p + 1)} disabled={page >= totalPages || loading}>
          Next ➡
        </button>
      </div>
    </div>
  );
}

export default AuditLogs;