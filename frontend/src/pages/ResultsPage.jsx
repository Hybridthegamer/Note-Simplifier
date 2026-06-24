import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../services/api";

export default function ResultsPage() {
  const { summaryId } = useParams();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("notes");
  const [generatingQuiz, setGeneratingQuiz] = useState(false);
  const [numQ, setNumQ] = useState(10);

  useEffect(() => {
    api.get(`/process/summary/${summaryId}`)
      .then(res => setSummary(res.data))
      .catch(() => toast.error("Failed to load results"))
      .finally(() => setLoading(false));
  }, [summaryId]);

  const handleGenerateQuiz = async () => {
    setGeneratingQuiz(true);
    try {
      const res = await api.post(`/quiz/generate/${summaryId}`, { num_questions: numQ });
      navigate(`/quiz/${res.data.quiz.id}`);
    } catch (err) {
      toast.error(err.response?.data?.error || "Quiz generation failed");
    } finally {
      setGeneratingQuiz(false);
    }
  };

  const downloadNotes = async (format) => {
    try {
      const res = await api.get(`/export/notes/${summaryId}/${format}`, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `notes.${format}`;
      a.click();
    } catch { toast.error("Download failed"); }
  };

  if (loading) return <div className="text-center mt-5"><div className="spinner-border text-primary" /></div>;
  if (!summary) return <div className="alert alert-danger">Summary not found.</div>;

  const badgeClass = { basic: "badge-basic", intermediate: "badge-intermediate", advanced: "badge-advanced" }[summary.complexity_level] || "bg-secondary";

  return (
    <div>
      <div className="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
        <div>
          <h4 className="fw-bold mb-0">Simplified Notes</h4>
          <span className={`badge ${badgeClass} mt-1`}>{summary.complexity_level}</span>
          <span className="text-muted small ms-2">{summary.word_count} words</span>
        </div>
        <div className="d-flex gap-2">
          <button className="btn btn-sm btn-outline-secondary" onClick={() => downloadNotes("pdf")}>
            <i className="bi bi-file-pdf me-1" />PDF
          </button>
          <button className="btn btn-sm btn-outline-secondary" onClick={() => downloadNotes("docx")}>
            <i className="bi bi-file-word me-1" />DOCX
          </button>
        </div>
      </div>

      <ul className="nav nav-tabs mb-4">
        {["notes", "concepts", "quiz"].map(tab => (
          <li key={tab} className="nav-item">
            <button className={`nav-link ${activeTab === tab ? "active" : ""}`}
              onClick={() => setActiveTab(tab)}>
              {{ notes: "📄 Simplified Notes", concepts: `🔑 Key Concepts (${summary.key_concepts?.length || 0})`, quiz: "🎯 Generate Quiz" }[tab]}
            </button>
          </li>
        ))}
      </ul>

      {activeTab === "notes" && (
        <div className="card p-4">
          <div className="simplified-text">{summary.simplified_text}</div>
        </div>
      )}

      {activeTab === "concepts" && (
        <div>
          {(!summary.key_concepts || summary.key_concepts.length === 0) ? (
            <div className="text-muted text-center p-4">No key concepts extracted.</div>
          ) : (
            <div className="row g-2">
              {summary.key_concepts.map((kc, i) => (
                <div key={i} className="col-md-6">
                  <div className="concept-card">
                    <div className="fw-semibold">{kc.term}</div>
                    {kc.definition && <div className="text-muted small mt-1">{kc.definition}</div>}
                    <span className="badge bg-light text-dark mt-1" style={{ fontSize: "0.7rem" }}>score: {kc.score}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "quiz" && (
        <div className="card p-4" style={{ maxWidth: 480 }}>
          <h6 className="fw-semibold mb-3">Generate Quiz from these notes</h6>
          <label className="form-label">Number of Questions: <strong>{numQ}</strong></label>
          <input type="range" className="form-range mb-3" min={5} max={20} value={numQ}
            onChange={e => setNumQ(Number(e.target.value))} />
          <div className="d-flex justify-content-between text-muted small mb-4"><span>5</span><span>20</span></div>
          <button className="btn btn-primary" onClick={handleGenerateQuiz} disabled={generatingQuiz}>
            {generatingQuiz ? <span className="spinner-border spinner-border-sm me-2" /> : <i className="bi bi-lightning-charge me-2" />}
            Generate {numQ} Questions
          </button>
        </div>
      )}
    </div>
  );
}
