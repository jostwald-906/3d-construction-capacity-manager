import React, { useState } from "react";
import client from "../api/client.js";
import { useAuth } from "../state/AuthContext.jsx";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username,setUsername]=useState("");
  const [password,setPassword]=useState("");
  const [error,setError]=useState("");
  const { setToken } = useAuth();
  const nav = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    try {
      const form = new URLSearchParams({ username, password });
      const { data } = await client.post("/auth/login", form);
      setToken(data.access_token);
      nav("/");
    } catch (err) {
      setError("Invalid login");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <form onSubmit={submit} className="bg-white shadow-xl rounded-2xl p-6 w-full max-w-sm space-y-4">
        <h1 className="text-xl font-bold text-center">Sign in</h1>
        <input className="w-full border rounded-lg p-2" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
        <input className="w-full border rounded-lg p-2" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <button className="w-full bg-blue-600 text-white rounded-lg p-2">Login</button>
      </form>
    </div>
  );
}
