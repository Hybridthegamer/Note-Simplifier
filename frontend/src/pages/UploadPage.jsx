import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../services/api";

const COMPLEXITY_LEVELS = [
  { value: "basic", label: "Basic", desc: "Simple language, everyday vocabulary" },
  { value: "intermediate", label: "Intermediate", desc: "Balanced simplification with brief explanations" },
  { value: "advanced", label: "Advanced", desc: "Technical terms preserved, condensed style" },
];

export default function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [rawText, setRawText] = useState("");
  const [inputMode, setInputMode] = useState("file");
  const [complexity, setComplexity] = useState("intermediate");
  const [numQuestions, setNumQuestions] = useState(10);
  const [includeKeywords, setIncludeKeywords] = useState(true);
  const [step, setStep] = useState("upload");
  const [processing, setProcessing] = useState(false);
  const [docId, setDocId] = useState(null);

  const onDrop = useCallback(acceptedFiles => {
    setFile(acceptedFiles[0] || null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"], "text/plain": [".txt"] },
    maxSize: 20 * 1024 * 1024,
    multiple: false,
    onDropRejected: () => toast.error("File rejected. Max 20 MB, PDF/DOCX/TXT only."),
  });

  const handleUpload = async () => {
    if (inputMode === "file" && !file) { toast.error("Please select a file"); return; }
    if (inputMode === "text" && rawText.trim().length < 50) { toast.error("Please enter at least 50 characters of text"); return; }

    setProcessing(true);
    try {
      let uploadedDocId;
      if (inputMode === "file") {
        const fd = new FormData();
        fd.append("file", file);
        const res = await api.post("/documents/upload", fd);
        uploadedDocId = res.data.document.id;
        toast.success("Document uploaded successfully");
      } else {
        const blob = new Blob([rawText], { type: "text/plain" });
        const fd = new FormData();
        fd.append("file", blob, "pasted-text.txt");
        const res = await api.post("/documents/upload", fd);
        uploadedDocId = res.data.document.id;
      }
      setDocId(uploadedDocId);
      setStep("configure");
    } catch (err) {
      toast.error(err.response?.data?.error || "Upload failed");
    } finally {
      setProcessing(false);
    }
  };

  const handleProcess = async () => {
    setProcessing(true);
    try {
      const res = await api.post(`/process/${docId}`, {
        complexity_level: complexity,
        include_keywords: includeKeywords,
      });
      toast.success("Processing complete!");
      navigate(`/results/${res.data.summary.id}`);
    } catch (err) {
      toast.error(err.response?.data?.error || "Processing failed");
    } finally {
      setProcessing(false);
    }
  };

  if (processing) {
    return (
      <div className="spinner-overlay">
        <div className="card p-4 text-center" style={{ minWidth: 260 }}>
          <div className="spinner-border text-primary mb-3 mx-auto" style={{ width: "3rem", height: "3rem" }} />
          <h6 className="fw-bold">
            {step === "upload" ? "Uploading document…" : "AI is processing your document…"}
          </h6>
          <p className="text-muted small mb-0">
            {step !== "upload" && "This may take 15–30 seconds depending on document length."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 720 }}>
      <h4 className="fw-bold mb-1">Upload Document</h4>
      <p className="text-muted mb-4">Upload or paste academic text to simplify and generate a quiz.</p>

      {step === "upload" && (
        <>
          <div className="btn-group mb-4" role="group">
            <button className={`btn btn-sm ${inputMode === "file" ? "btn-primary" : "btn-outline-secondary"}`}
              onClick={() => setInputMode("file")}><i className="bi bi-file-earmark me-1" />File Upload</button>
            <button className={`btn btn-sm ${inputMode === "text" ? "btn-primary" : "btn-outline-secondary"}`}
              onClick={() => setInputMode("text")}><i className="bi bi-textarea-t me-1" />Paste Text</button>
          </div>

          {inputMode === "file" ? (
            <div {...getRootProps()} className={`upload-zone mb-4 ${isDragActive ? "drag-active" : ""}`}>
              <input {...getInputProps()} />
              <i className="bi bi-cloud-arrow-up fs-1 text-primary mb-3 d-block" />
              {file ? (
                <div>
                  <div className="fw-semibold">{file.name}</div>
                  <div className="text-muted small">{(file.size / 1024).toFixed(1)} KB</div>
                </div>
              ) : (
                <div>
                  <div className="fw-semibold mb-1">Drag & drop or click to select</div>
                  <div className="text-muted small">PDF, DOCX, or TXT · Max 20 MB</div>
                </div>
              )}
            </div>
          ) : (
            <textarea className="form-control mb-4" rows={12} placeholder="Paste your academic text here…"
              value={rawText} onChange={e => setRawText(e.target.value)} />
          )}

          <button className="btn btn-primary" onClick={handleUpload}
            disabled={inputMode === "file" ? !file : rawText.trim().length < 50}>
            <i className="bi bi-arrow-right-circle me-2" />Continue
          </button>
        </>
      )}

      {step === "configure" && (
        <>
          <div className="card p-4 mb-4">
            <h6 className="fw-semibold mb-3">Simplification Level</h6>
            <div className="d-flex flex-column gap-2">
              {COMPLEXITY_LEVELS.map(({ value, label, desc }) => (
                <label key={value} className={`quiz-option d-flex align-items-center gap-3 ${complexity === value ? "selected" : ""}`}>
                  <input type="radio" name="complexity" value={value}
                    checked={complexity === value} onChange={() => setComplexity(value)} />
                  <div>
                    <div className="fw-semibold">{label}</div>
                    <div className="text-muted small">{desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="card p-4 mb-4">
            <h6 className="fw-semibold mb-3">Quiz Questions: <span className="text-primary">{numQuestions}</span></h6>
            <input type="range" className="form-range" min={5} max={20} value={numQuestions}
              onChange={e => setNumQuestions(Number(e.target.value))} />
            <div className="d-flex justify-content-between text-muted small"><span>5</span><span>20</span></div>
          </div>

          <div className="card p-4 mb-4">
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="kwSwitch"
                checked={includeKeywords} onChange={e => setIncludeKeywords(e.target.checked)} />
              <label className="form-check-label fw-semibold" htmlFor="kwSwitch">
                Extract Key Concepts
              </label>
              <div className="text-muted small">AI identifies and defines key academic terms</div>
            </div>
          </div>

          <div className="d-flex gap-2">
            <button className="btn btn-outline-secondary" onClick={() => setStep("upload")}>
              <i className="bi bi-arrow-left me-1" />Back
            </button>
            <button className="btn btn-primary" onClick={handleProcess}>
              <i className="bi bi-cpu me-2" />Process Document
            </button>
          </div>
        </>
      )}
    </div>
  );
}
