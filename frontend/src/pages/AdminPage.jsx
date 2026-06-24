import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import api from "../services/api";

export default function AdminPage() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [activeTab, setActiveTab] = useState("stats");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get("/admin/stats"), api.get("/admin/users")])
      .then(([statsRes, usersRes]) => { setStats(statsRes.data); setUsers(usersRes.data); })
      .catch(() => toast.error("Failed to load admin data"))
      .finally(() => setLoading(false));
  }, []);

  const deleteUser = async userId => {
    if (!confirm("Delete this user?")) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      setUsers(prev => prev.filter(u => u.id !== userId));
      toast.success("User deleted");
    } catch (err) {
      toast.error(err.response?.data?.error || "Delete failed");
    }
  };

  if (loading) return <div className="text-center mt-5"><div className="spinner-border text-primary" /></div>;

  return (
    <div>
      <h4 className="fw-bold mb-4">Admin Panel</h4>

      <ul className="nav nav-tabs mb-4">
        {["stats", "users"].map(tab => (
          <li key={tab} className="nav-item">
            <button className={`nav-link ${activeTab === tab ? "active" : ""}`} onClick={() => setActiveTab(tab)}>
              {{ stats: "📊 System Stats", users: `👥 Users (${users.length})` }[tab]}
            </button>
          </li>
        ))}
      </ul>

      {activeTab === "stats" && stats && (
        <div className="row g-3">
          {[
            { label: "Total Users", value: stats.total_users, icon: "bi-people" },
            { label: "Total Documents", value: stats.total_documents, icon: "bi-files" },
            { label: "Total Summaries", value: stats.total_summaries, icon: "bi-file-text" },
            { label: "Total Quizzes", value: stats.total_quizzes, icon: "bi-question-circle" },
          ].map(({ label, value, icon }) => (
            <div className="col-md-3" key={label}>
              <div className="card p-3 text-center">
                <i className={`bi ${icon} fs-2 text-primary mb-2`} />
                <div className="fw-bold fs-3">{value}</div>
                <div className="text-muted small">{label}</div>
              </div>
            </div>
          ))}
          <div className="col-12">
            <div className="card p-4">
              <h6 className="fw-semibold mb-3">Document Processing Status</h6>
              <div className="row g-2">
                {Object.entries(stats.documents_by_status).map(([status, count]) => (
                  <div className="col-sm-3" key={status}>
                    <div className="text-center p-2 rounded" style={{ background: "var(--highlight)" }}>
                      <div className="fw-bold">{count}</div>
                      <div className="text-muted small text-capitalize">{status}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "users" && (
        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover mb-0">
              <thead className="table-light">
                <tr>
                  <th>Name</th><th>Email</th><th>Role</th><th>Joined</th><th>Last Login</th><th></th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td className="fw-semibold">{u.full_name}</td>
                    <td>{u.email}</td>
                    <td><span className={`badge ${u.role === "admin" ? "bg-danger" : "bg-secondary"}`}>{u.role}</span></td>
                    <td className="text-muted small">{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
                    <td className="text-muted small">{u.last_login ? new Date(u.last_login).toLocaleDateString() : "Never"}</td>
                    <td>
                      {u.role !== "admin" && (
                        <button className="btn btn-sm btn-outline-danger" onClick={() => deleteUser(u.id)}>
                          <i className="bi bi-trash" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
