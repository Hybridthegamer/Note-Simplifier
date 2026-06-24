import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../services/api";

const LABELS = ["A", "B", "C", "D"];

export default function QuizPage() {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState(null);
  const [current, setCurrent] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    api.get(`/quiz/${quizId}`)
      .then(res => {
        setQuiz(res.data);
        setAnswers(new Array(res.data.questions.length).fill(null));
      })
      .catch(() => toast.error("Failed to load quiz"))
      .finally(() => setLoading(false));
  }, [quizId]);

  const select = idx => {
    if (submitted) return;
    setAnswers(prev => { const a = [...prev]; a[current] = idx; return a; });
  };

  const handleSubmit = async () => {
    if (answers.some(a => a === null)) {
      toast.warn("Please answer all questions before submitting");
      return;
    }
    setSubmitting(true);
    try {
      const res = await api.post(`/quiz/${quizId}/submit`, { answers });
      setResults(res.data);
      setSubmitted(true);
    } catch (err) {
      toast.error(err.response?.data?.error || "Submission failed");
    } finally {
      setSubmitting(false);
    }
  };

  const downloadQuiz = async (format) => {
    try {
      const res = await api.get(`/export/quiz/${quizId}/${format}`, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url; a.download = `quiz.${format}`; a.click();
    } catch { toast.error("Download failed"); }
  };

  if (loading) return <div className="text-center mt-5"><div className="spinner-border text-primary" /></div>;
  if (!quiz) return <div className="alert alert-danger">Quiz not found.</div>;

  if (submitted && results) {
    const pct = results.score;
    return (
      <div style={{ maxWidth: 720 }}>
        <h4 className="fw-bold mb-4">Quiz Results</h4>
        <div className="card p-4 mb-4 text-center">
          <div className="score-ring mx-auto mb-3" style={{ "--pct": `${pct}%` }}>
            <span>{pct}%</span>
          </div>
          <h5 className="fw-bold">{results.correct} / {results.total} correct</h5>
          <div className={`badge ${results.passed ? "bg-success" : "bg-danger"} fs-6 mt-1`}>
            {results.passed ? "PASSED ✓" : "NOT PASSED ✗"}
          </div>
          <div className="text-muted small mt-2">Pass threshold: {results.pass_threshold}%</div>
          <div className="text-muted small">Time: {Math.round((Date.now() - startTime) / 1000)}s</div>
          <div className="d-flex justify-content-center gap-2 mt-3">
            <button className="btn btn-sm btn-outline-secondary" onClick={() => downloadQuiz("pdf")}>
              <i className="bi bi-file-pdf me-1" />Download PDF
            </button>
            <button className="btn btn-sm btn-outline-secondary" onClick={() => downloadQuiz("docx")}>
              <i className="bi bi-file-word me-1" />Download DOCX
            </button>
          </div>
        </div>

        <h6 className="fw-semibold mb-3">Review</h6>
        {results.results.map((r, i) => (
          <div key={i} className={`card p-3 mb-2 border-${r.correct ? "success" : "danger"}`}>
            <div className="fw-semibold small mb-2">Q{i + 1}. {r.question}</div>
            {quiz.questions[i].options.map((opt, j) => (
              <div key={j} className={`quiz-option small py-2 px-3 ${
                j === r.correct_index ? "correct" : j === r.selected && !r.correct ? "incorrect" : ""
              }`}>
                <strong>{LABELS[j]}.</strong> {opt}
                {j === r.correct_index && <i className="bi bi-check-circle-fill text-success ms-2" />}
                {j === r.selected && !r.correct && <i className="bi bi-x-circle-fill text-danger ms-2" />}
              </div>
            ))}
            {r.explanation && <div className="text-muted small mt-2 ps-2"><i className="bi bi-info-circle me-1" />{r.explanation}</div>}
          </div>
        ))}
        <button className="btn btn-outline-primary mt-2" onClick={() => navigate("/dashboard")}>
          <i className="bi bi-house me-1" />Back to Dashboard
        </button>
      </div>
    );
  }

  const q = quiz.questions[current];
  const answered = answers.filter(a => a !== null).length;

  return (
    <div style={{ maxWidth: 680 }}>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="fw-bold mb-0">Quiz</h4>
        <span className="text-muted small">{answered}/{quiz.questions.length} answered</span>
      </div>

      <div className="progress mb-4" style={{ height: 6 }}>
        <div className="progress-bar bg-primary" style={{ width: `${((current + 1) / quiz.questions.length) * 100}%` }} />
      </div>

      <div className="card p-4 mb-4">
        <div className="text-muted small mb-2">Question {current + 1} of {quiz.questions.length}</div>
        <div className="fw-semibold mb-3" style={{ fontSize: "1.05rem" }}>{q.question}</div>
        {q.options.map((opt, i) => (
          <div key={i}
            className={`quiz-option ${answers[current] === i ? "selected" : ""}`}
            onClick={() => select(i)}>
            <strong className="me-2">{LABELS[i]}.</strong>{opt}
          </div>
        ))}
      </div>

      <div className="d-flex justify-content-between">
        <button className="btn btn-outline-secondary" disabled={current === 0}
          onClick={() => setCurrent(c => c - 1)}>
          <i className="bi bi-arrow-left me-1" />Previous
        </button>
        {current < quiz.questions.length - 1 ? (
          <button className="btn btn-primary" onClick={() => setCurrent(c => c + 1)}>
            Next <i className="bi bi-arrow-right ms-1" />
          </button>
        ) : (
          <button className="btn btn-success" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <span className="spinner-border spinner-border-sm me-2" /> : null}
            Submit Quiz
          </button>
        )}
      </div>

      <div className="d-flex flex-wrap gap-1 mt-4">
        {quiz.questions.map((_, i) => (
          <button key={i}
            className={`btn btn-sm ${i === current ? "btn-primary" : answers[i] !== null ? "btn-success" : "btn-outline-secondary"}`}
            style={{ width: 36, height: 36, padding: 0 }}
            onClick={() => setCurrent(i)}>
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  );
}
