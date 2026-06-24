import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    if (form.password !== form.confirm) { toast.error("Passwords do not match"); return; }
    setLoading(true);
    try {
      await register(form.full_name, form.email, form.password);
      toast.success("Account created!");
      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.error || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const f = (field, val) => setForm({ ...form, [field]: val });

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center" style={{ background: "var(--bg)" }}>
      <div className="card p-4" style={{ width: "100%", maxWidth: 440 }}>
        <div className="text-center mb-4">
          <i className="bi bi-book-half fs-1 text-primary" />
          <h4 className="fw-bold mt-2" style={{ color: "var(--primary)" }}>Create Account</h4>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label fw-semibold">Full Name</label>
            <input className="form-control" value={form.full_name}
              onChange={e => f("full_name", e.target.value)} required />
          </div>
          <div className="mb-3">
            <label className="form-label fw-semibold">Email</label>
            <input type="email" className="form-control" value={form.email}
              onChange={e => f("email", e.target.value)} required />
          </div>
          <div className="mb-3">
            <label className="form-label fw-semibold">Password</label>
            <input type="password" className="form-control" value={form.password}
              onChange={e => f("password", e.target.value)} required />
            <small className="text-muted">Min 8 chars, 1 uppercase, 1 number, 1 special character</small>
          </div>
          <div className="mb-4">
            <label className="form-label fw-semibold">Confirm Password</label>
            <input type="password" className="form-control" value={form.confirm}
              onChange={e => f("confirm", e.target.value)} required />
          </div>
          <button className="btn btn-primary w-100" disabled={loading}>
            {loading ? <span className="spinner-border spinner-border-sm me-2" /> : null}
            Create Account
          </button>
        </form>
        <p className="text-center mt-3 small">
          Already have an account? <Link to="/login">Sign In</Link>
        </p>
      </div>
    </div>
  );
}
