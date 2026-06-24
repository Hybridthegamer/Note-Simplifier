import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../services/api";

export default function HistoryPage() {
  const [docs, setDocs] = useState([]);
  const [summaries, setSummaries] = useState({});
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/documents/")
      .then(res => setDocs(res.data))
      .catch(() => toast.error("Failed to load history"))
      .finally(() => setLoading(false));
  }, []);

  const loadSummaries = async docId => {
    if (summaries[docId]) { setExpanded(expanded === docId ? null : docId); return; }
    try {
      const res = await api.get(`/process/${docId}/summaries`);
      setSummaries(prev => ({ ...prev, [docId]: res.data }));
      setExpanded(docId);
    } catch { toast.error("Failed to load summaries"); }
  };

  const deleteDoc = async (docId, e) => {
    e.stopPropagation();
    if (!confirm("Delete this document and all its summaries?")) return;
    try {
      await api.delete(`/documents/${docId}`);
      setDocs(prev => prev.filter(d => d.id !== docId));
      toast.success("Deleted");
    } catch { toast.error("Delete failed"); }
  };

  if (loading) return <div className="text-center mt-5"><div className="spinner-border text-primary" /></div>;

  return (
    <div>
      <h4 className="fw-bold mb-1">Study History</h4>
      <p className="text-muted mb-4">All your uploaded documents and generated summaries.</p>

      {docs.length === 0 ? (
        <div className="text-center p-5 text-muted">
          <i className="bi bi-inbox fs-1 d-block mb-2" />
          No documents yet — <Link to="/upload">upload your first one</Link>
        </div>
      ) : (
        <div className="d-flex flex-column gap-3">
          {docs.map(doc => (
            <div key={doc.id} className="card">
              <div className="card-body d-flex align-items-center justify-content-between"
                style={{ cursor: doc.status === "processed" ? "pointer" : "default" }}
                onClick={() => doc.status === "processed" && loadSummaries(doc.id)}>
                <div className="d-flex align-items-center gap-3">
                  <i className="bi bi-file-earmark-text fs-3 text-primary" />
                  <div>
                    <div className="fw-semibold">{doc.original_filename}</div>
                    <div className="text-muted small">
                      {new Date(doc.upload_date).toLocaleDateString()} · {doc.file_size_kb.toFixed(1)} KB · {doc.file_type.toUpperCase()}
                    </div>
                  </div>
                </div>
                <div className="d-flex align-items-center gap-2">
                  <span className={`badge ${statusBadge(doc.status)}`}>{doc.status}</span>
                  {doc.status === "uploaded" && (
                    <Link to="/upload" className="btn btn-sm btn-primary" onClick={e => e.stopPropagation()}>
                      Process
                    </Link>
                  )}
                  <button className="btn btn-sm btn-outline-danger" onClick={e => deleteDoc(doc.id, e)}>
                    <i className="bi bi-trash" />
                  </button>
                  {doc.status === "processed" && (
                    <i className={`bi bi-chevron-${expanded === doc.id ? "up" : "down"} text-muted`} />
                  )}
                </div>
              </div>

              {expanded === doc.id && summaries[doc.id] && (
                <div className="border-top px-3 py-2">
                  {summaries[doc.id].length === 0 ? (
                    <div className="text-muted small p-2">No summaries generated yet.</div>
                  ) : (
                    summaries[doc.id].map(s => (
                      <Link key={s.id} to={`/results/${s.id}`}
                        className="d-flex align-items-center justify-content-between p-2 rounded text-decoration-none hover-highlight"
                        style={{ color: "inherit" }}>
                        <div>
                          <span className={`badge me-2 ${badgeClass(s.complexity_level)}`}>{s.complexity_level}</span>
                          <span className="text-muted small">{s.word_count} words · {new Date(s.created_at).toLocaleDateString()}</span>
                        </div>
                        <i className="bi bi-arrow-right text-muted" />
                      </Link>
                    ))
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function statusBadge(status) {
  return { uploaded: "bg-secondary", processing: "bg-warning text-dark", processed: "bg-success", error: "bg-danger" }[status] || "bg-secondary";
}
function badgeClass(level) {
  return { basic: "badge-basic", intermediate: "badge-intermediate", advanced: "badge-advanced" }[level] || "bg-secondary";
}
