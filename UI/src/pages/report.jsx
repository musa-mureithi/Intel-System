import React, { useState, useEffect } from "react";
import "../App.css";

const BASE_URL = "http://127.0.0.1:8000";

function Report() {
  const [formData, setFormData] = useState({
    operation_id: "",
    subject: "",
    content: "",
    role_based_access: "",
  });

  const [operations, setOperations] = useState([]);
  const [reports, setReports] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Fetch reports and operations on mount
  useEffect(() => {
    fetchOperations();
    fetchReports();
  }, []);

  // Fetch all operations for dropdown
  const fetchOperations = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("No token found.");

      const res = await fetch(`${BASE_URL}/operation/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setOperations(data);
    } catch (err) {
      setError(err.message);
    }
  };

  // Fetch all reports
  const fetchReports = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("No token found.");

      const res = await fetch(`${BASE_URL}/list_reports/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setReports(data.reports || []);
    } catch (err) {
      setError(err.message);
    }
  };

  // Handle form input changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle create/update report
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("No token found.");

      const url = editingId
        ? `${BASE_URL}/report/${editingId}/`
        : `${BASE_URL}/create_report/`;
      const method = editingId ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed to submit report");

      setMessage(editingId ? "Report updated successfully." : "Report created successfully.");
      setFormData({ operation_id: "", subject: "", content: "", role_based_access: "" });
      setEditingId(null);
      fetchReports(); // Refresh report list
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle delete report
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this report?")) return;

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BASE_URL}/report/${id}/`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed to delete report");

      setMessage("Report deleted successfully.");
      setReports(reports.filter((r) => r.id !== id));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle edit report (prefill form)
  const handleEdit = (report) => {
    setFormData({
      operation_id: report.operation_id,
      subject: report.subject,
      content: report.content,
      role_based_access: report.role_based_access,
    });
    setEditingId(report.id);
  };

  return (
    <div className="report-container">
      <h2 className="title">Report Manager</h2>

      {/* Form */}
      <form className="form" onSubmit={handleSubmit}>
        <select
          name="operation_id"
          value={formData.operation_id}
          onChange={handleChange}
          required
        >
          <option value="">Select Operation</option>
          {operations.map((op) => (
            <option key={op.id} value={op.id}>
              {op.mission_name}
            </option>
          ))}
        </select>

        <input
          type="text"
          name="subject"
          placeholder="Subject"
          value={formData.subject}
          onChange={handleChange}
          required
        />

        <textarea
          name="content"
          placeholder="Report Content"
          value={formData.content}
          onChange={handleChange}
          required
        />

         <select name="Role-Based Access" value={formData.clearance_type} onChange={handleChange}>
          <option value="TOP-SECRET">TOP-SECRET</option>
          <option value="SECRET">SECRET</option>
          <option value="CONFIDENTIAL">CONFIDENTIAL</option>
          <option value="UNCLASSIFIED">UNCLASSIFIED</option>
        </select>

        <button type="submit" disabled={loading}>
          {editingId ? "Update Report" : "Create Report"}
        </button>
      </form>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      {/* Report Table */}
      <h3 className="subtitle">Report List</h3>
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Operation</th>
            <th>Subject</th>
            <th>Content</th>
            <th>Role-Based Access</th>
            <th>Author</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((r) => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{r.operation}</td>
              <td>{r.subject}</td>
              <td>{r.content}</td>
              <td>{r.role_based_access}</td>
              <td>{r.author}</td>

              <td>
                <button onClick={() => handleEdit(r)}>Edit</button>
                <button onClick={() => handleDelete(r.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Report;