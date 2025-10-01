import React, { useEffect, useState } from "react";
import client from "../api/client.js";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const [projects,setProjects]=useState([]);
  const [models,setModels]=useState([]);

  useEffect(() => {
    (async () => {
      const p = await client.get("/projects");
      setProjects(p.data);
      const m = await client.get("/models");
      setModels(m.data);
    })();
  }, []);

  return (
    <div className="p-4 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <span className="text-sm text-gray-500">Mobile-friendly</span>
      </header>

      <section>
        <h2 className="font-semibold mb-2">Models</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {models.map(m => (
            <Link key={m.id} to={`/model/${m.id}`} className="block bg-white rounded-2xl shadow p-4 hover:shadow-lg">
              <div className="text-lg font-semibold">{m.name}</div>
              <div className="text-xs text-gray-500">Format: {m.format || "mock"}</div>
              <div className="text-xs text-gray-500">Bounds: [{m.min_x},{m.max_x}] x [{m.min_y},{m.max_y}] x [{m.min_z},{m.max_z}]</div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
