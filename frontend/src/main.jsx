import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./index.css";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ModelView from "./pages/ModelView.jsx";
import Projects from "./pages/Projects.jsx";
import Models from "./pages/Models.jsx";
import { AuthProvider, useAuth } from "./state/AuthContext.jsx";

function Protected({ children }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login/>} />
          <Route path="/" element={<Protected><Dashboard/></Protected>} />
          <Route path="/projects" element={<Protected><Projects/></Protected>} />
          <Route path="/models" element={<Protected><Models/></Protected>} />
          <Route path="/model/:id" element={<Protected><ModelView/></Protected>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
