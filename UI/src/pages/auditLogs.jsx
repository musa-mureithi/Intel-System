
import { useEffect, useState } from "react";
import "../App.css";

const BASE_URL = "https://75lsvb8q-8000.inc1.devtunnels.ms";

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedLog, setSelectedLog] = useState(null);

  const fetchLogs = async (pageNumber = 1) => {
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("You are not logged in.");
      }

      const response = await fetch(
        `${BASE_URL}/api/audit/get_logs/?page=${pageNumber}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.status === 401) {
        throw new Error("Session expired. Please log in again.");
      }

      if (response.status === 403) {
        throw new Error("Access denied. Superuser only.");
      }

      if (!response.ok) {
        throw new Error("Failed to fetch audit logs.");
      }

      const data = await response.json();

      setLogs(data.results || []);
      setPage(data.page || 1);
      setTotalPages(data.total_pages || 1);

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
      case "view":
        return "action-view";
      case "login":
        return "action-login";
      case "logout":
        return "action-logout";
      default:
        return "action-default";
    }
  };

  const formatTime = (time) => {
    if (!time) return "N/A";

    const date = new Date(time);

    return isNaN(date.getTime())
      ? "N/A"
      : date.toLocaleString();
  };

  return (
    <div className="audit-container">

      <h2 className="audit-title">Audit Logs</h2>

      {error && (
        <div className="audit-error">{error}</div>
      )}

      {loading && <p>Loading logs...</p>}

      {!loading && (
        <div className="audit-table-wrapper">

          <table className="audit-table">

            <thead>
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Resource ID</th>
                <th>IP</th>
                <th>Time</th>
                <th>Description</th>
              </tr>
            </thead>

            <tbody>
              {logs.length > 0 ? (
                logs.map((log) => (
                  <tr key={log.id}>

                    {/* Clickable audit ID */}
                    <td>
                      <button
                        className="audit-id-button"
                        onClick={() => setSelectedLog(log)}
                      >
                        #{log.id}
                      </button>
                    </td>

                    <td>{log.user || "Unknown"}</td>

                    <td>
                      <span className={getActionClass(log.action)}>
                        {log.action}
                      </span>
                    </td>

                    <td>{log.resource || "N/A"}</td>

                    <td>{log.resource_id || "N/A"}</td>

                    <td>{log.ip || "N/A"}</td>

                    <td>{formatTime(log.time)}</td>

                   {/* <td>{log.description || "No description"}</td>*/}

                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="audit-empty">
                    No logs found
                  </td>
                </tr>
              )}
            </tbody>

          </table>
        </div>
      )}

      {/* Pagination */}
      <div className="audit-pagination">

        <button
          onClick={() => setPage((p) => p - 1)}
          disabled={page <= 1 || loading}
        >
          ⬅ Prev
        </button>

        <span>
          Page {page} of {totalPages}
        </span>

        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={page >= totalPages || loading}
        >
          Next ➡
        </button>

      </div>

      {/* Audit Details Modal */}
      {selectedLog && (
        <div
          className="audit-modal-overlay"
          onClick={() => setSelectedLog(null)}
        >

          <div
            className="audit-modal"
            onClick={(e) => e.stopPropagation()}
          >

            <div className="audit-modal-header">
              <h2>Audit Log #{selectedLog.id}</h2>

              <button
                onClick={() => setSelectedLog(null)}
                className="audit-close"
              >
                ✕
              </button>
            </div>

            <div className="audit-modal-body">

              <h3>Activity Information</h3>

              <p><strong>User:</strong> {selectedLog.user}</p>

              <p><strong>Action:</strong> {selectedLog.action}</p>

              <p><strong>Resource:</strong> {selectedLog.resource}</p>

              <p><strong>Resource ID:</strong> {selectedLog.resource_id}</p>

              <p><strong>IP Address:</strong> {selectedLog.ip}</p>

              <p><strong>Time:</strong> {formatTime(selectedLog.time)}</p>

              <p>
                <strong>Description:</strong>{" "}
                {selectedLog.description || "No description available"}
              </p> 

              <hr />

              <h3>Previous Data</h3>

              <pre>
                {selectedLog.old_data
                  ? JSON.stringify(selectedLog.old_data, null, 2)
                  : "No previous data recorded"}
              </pre>

              <h3>New Data</h3>

              <pre>
                {selectedLog.new_data
                  ? JSON.stringify(selectedLog.new_data, null, 2)
                  : "No new data recorded"}
              </pre>
              <h4>Request Data</h4>
              
              <pre>
                {JSON.stringify(selectedLog.request_data, null, 2) ||
                  "No request data recorded"}
              </pre>

              <h4>Response Data</h4>
              <pre>
                {JSON.stringify(selectedLog.response_data, null, 2) ||
                  "No response data recorded"}
              </pre>

            </div>

            <div className="audit-modal-footer">
              <button onClick={() => setSelectedLog(null)}>
                Close
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

export default AuditLogs;
