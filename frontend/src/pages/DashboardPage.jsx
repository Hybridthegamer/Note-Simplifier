import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/documents/").then(res => setDocs(res.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const processed = docs.filter(d => d.status === "processed").length;
  const pending = docs.filter(d => d.status === "uploaded").length;

  return (
    <div>
      <div className="mb-4">
        <h4 className="fw-bold mb-0">Welcome back, {user?.full_name?.split(" ")[0]} 👋</h4>
        <p className="text-muted">Ready to simplify your study materials?</p>
      </div>

      <div className="row g-3 mb-4">
        {[
          { label: "Total Documents", value: docs.length, icon: "bi-file-earmark-text", color: "#ebf4ff" },
          { label: "Processed", value: processed, icon: "bi-check-circle", color: "#f0fff4" },
          { label: "Pending", value: pending, icon: "bi-hourglass-split", color: "#fffff0" },
        ].map(({ label, value, icon, color }) => (
          <div className="col-md-4" key={label}>
            <div className="card p-3 h-100" style={{ background: color }}>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="text-muted small">{label}</div>
                  <div className="fw-bold fs-3">{value}</div>
                </div>
                <i className={`bi ${icon} fs-2 opacity-25`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="d-flex gap-3 mb-4">
        <Link to="/upload" className="btn btn-primary">
          <i className="bi bi-cloud-upload me-2" />Upload Document
        </Link>
        <Link to="/history" className="btn btn-outline-secondary">
          <i className="bi bi-clock-history me-2" />Study History
        </Link>
      </div>

      <div className="card">
        <div className="card-header bg-white fw-semibold border-bottom">Recent Documents</div>
        {loading ? (
          <div className="text-center p-4"><div className="spinner-border text-primary" /></div>
        ) : docs.length === 0 ? (
          <div className="text-center p-5 text-muted">
            <i className="bi bi-inbox fs-1 d-block mb-2" />
            No documents yet — <Link to="/upload">upload your first one</Link>
          </div>
        ) : (
          <div className="list-group list-group-flush">
            {docs.slice(0, 8).map(doc => (
              <div key={doc.id} className="list-group-item d-flex align-items-center justify-content-between">
                <div className="d-flex align-items-center gap-2">
                  <i className="bi bi-file-earmark-text text-primary fs-5" />
                  <div>
                    <div className="fw-semibold small">{doc.original_filename}</div>
                    <div className="text-muted" style={{ fontSize: "0.78rem" }}>
                      {new Date(doc.upload_date).toLocaleDateString()} · {doc.file_size_kb.toFixed(1)} KB
                    </div>
                  </div>
                </div>
                <span className={`badge ${statusBadge(doc.status)}`}>{doc.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function statusBadge(status) {
  return { uploaded: "bg-secondary", processing: "bg-warning text-dark", processed: "bg-success", error: "bg-danger" }[status] || "bg-secondary";
}
