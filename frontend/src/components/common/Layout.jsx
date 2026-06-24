import React, { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const navItems = [
  { to: "/dashboard", icon: "bi-house", label: "Dashboard" },
  { to: "/upload", icon: "bi-cloud-upload", label: "Upload Document" },
  { to: "/history", icon: "bi-clock-history", label: "Study History" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div>
      <nav className="sidebar d-flex flex-column">
        <div className="nav-brand mb-4 ps-1">
          <i className="bi bi-book-half me-2" />
          NoteSimplifier
        </div>

        <div className="flex-grow-1">
          {navItems.map(({ to, icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `sidebar-link mb-1 ${isActive ? "active" : ""}`}>
              <i className={`bi ${icon}`} /> {label}
            </NavLink>
          ))}
          {user?.role === "admin" && (
            <NavLink to="/admin" className={({ isActive }) => `sidebar-link mb-1 ${isActive ? "active" : ""}`}>
              <i className="bi bi-shield-check" /> Admin
            </NavLink>
          )}
        </div>

        <div className="mt-auto pt-3 border-top border-light border-opacity-25">
          <div className="px-1 mb-2">
            <div className="text-white fw-semibold small">{user?.full_name}</div>
            <div className="text-white-50 small">{user?.email}</div>
          </div>
          <button onClick={handleLogout} className="btn btn-sm btn-outline-light w-100">
            <i className="bi bi-box-arrow-right me-1" /> Logout
          </button>
        </div>
      </nav>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
