import React, { useState, useEffect } from "react";
import "../App.css";

const BASE_URL = "http://127.0.0.1:8000";

const Operation = () => {
  const [formData, setFormData] = useState({
    identity_number: "",
    mission_name: "",
    description: "",
    Assigned_Personnel: "",
    clearance_type: "SECRET",
  });
  const [operations, setOperations] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchOperations();
  }, []);

  const fetchOperations = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("No token found.");

      const res = await fetch(`${BASE_URL}/operation/`, {
        method: "GET",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed to fetch operations");

      setOperations(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("No token found.");

      const url = editingId ? `${BASE_URL}/operation/${editingId}/` : `${BASE_URL}/operation/`;
      const method = editingId ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed to save operation");

      setMessage(editingId ? "Updated successfully" : "Created successfully");
      setFormData({ identity_number: "", mission_name: "", description: "", Assigned_Personnel: "", clearance_type: "SECRET" });
      setEditingId(null);
      fetchOperations();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (op) => {
    setFormData({
      identity_number: op.identity_number,
      mission_name: op.mission_name,
      description: op.description,
      Assigned_Personnel: op.Assigned_Personnel.map(p => p.full_name).join(", "),
      clearance_type: op.clearance_type,
    });
    setEditingId(op.id);
  };

  return (
    <div className="container">
      <h2 className="title">Operation Manager</h2>
      <form className="form" onSubmit={handleSubmit}>
        <input name="identity_number" placeholder="Identity Number" value={formData.identity_number} onChange={handleChange} required />
        <input name="mission_name" placeholder="Mission Name" value={formData.mission_name} onChange={handleChange} required />
        <textarea name="description" placeholder="Description" value={formData.description} onChange={handleChange} required />
        <textarea name="Assigned_Personnel" placeholder="Enter names separated by commas" value={formData.Assigned_Personnel} onChange={handleChange} required />
        <select name="clearance_type" value={formData.clearance_type} onChange={handleChange}>
          <option value="TOP-SECRET">TOP-SECRET</option>
          <option value="SECRET">SECRET</option>
          <option value="CLASSIFIED">CLASSIFIED</option>
          <option value="CONFIDENTIAL">CONFIDENTIAL</option>
          <option value="UNCLASSIFIED">UNCLASSIFIED</option>
        </select>
        <button className="btn" type="submit">{loading ? "Saving..." : editingId ? "Update" : "Create"}</button>
      </form>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <h3 className="subtitle">Operations List</h3>
      <div className="list">
        {operations.length === 0 ? <p>No operations found.</p> : operations.map(op => (
          <div key={op.id} className="card">
            <h4>{op.mission_name}</h4>
            <p>Assigned Personnel: {op.Assigned_Personnel.map(p => p.full_name).join(", ")}</p>
            <p>External: {op.external_personnel.join(", ")}</p>
            <p>{op.description}</p>
            <p>Created by: {op.created_by?.full_name} ({op.created_by?.person_type})</p>
            {op.updated_by?.full_name && <p>Last updated by: {op.updated_by.full_name} ({op.updated_by.person_type})</p>}
            <span className="badge">{op.clearance_type}</span>
            <button className="edit-btn" onClick={() => handleEdit(op)}>Edit</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Operation;