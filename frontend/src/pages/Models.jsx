import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client.js";

export default function Models() {
  const [models, setModels] = useState([]);
  const [projects, setProjects] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    project_id: "",
    name: "",
    file: null,
    additionalFiles: []
  });

  useEffect(() => {
    loadModels();
    loadProjects();
  }, []);

  const loadModels = async () => {
    try {
      const res = await client.get("/models");
      setModels(res.data);
    } catch (error) {
      console.error("Failed to load models:", error);
    }
  };

  const loadProjects = async () => {
    try {
      const res = await client.get("/projects");
      setProjects(res.data);
    } catch (error) {
      console.error("Failed to load projects:", error);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const ext = file.name.split('.').pop().toLowerCase();
      const supported = ['obj', 'gltf', 'glb', 'stl', 'ply', 'dae'];
      if (!supported.includes(ext)) {
        alert("Please upload a supported 3D model file (OBJ, GLTF, GLB, STL, PLY, or DAE). FBX files should be converted to OBJ or GLTF using Blender first.");
        e.target.value = "";
        return;
      }
      setFormData({ ...formData, file, name: formData.name || file.name.replace(/\.[^/.]+$/, "") });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.file) {
      alert("Please select a 3D model file");
      return;
    }

    setUploading(true);
    try {
      // Create FormData for file upload
      const data = new FormData();
      data.append("file", formData.file);
      data.append("project_id", formData.project_id);
      data.append("name", formData.name);

      // Add additional files (for GLTF .bin files, textures, etc.)
      formData.additionalFiles.forEach((file) => {
        data.append("additional_files", file);
      });

      await client.post("/models/upload", data, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      loadModels();
      resetForm();
      alert("Model uploaded successfully! Grid will be generated automatically.");
    } catch (error) {
      console.error("Failed to upload model:", error);
      alert("Failed to upload model: " + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Are you sure you want to delete this model? This will also delete all associated grid cells and allocations.")) return;

    try {
      await client.delete(`/models/${id}`);
      loadModels();
    } catch (error) {
      console.error("Failed to delete model:", error);
      alert("Failed to delete model. Make sure you have admin permissions.");
    }
  };

  const resetForm = () => {
    setFormData({ project_id: "", name: "", file: null, additionalFiles: [] });
    setShowForm(false);
  };

  const handleAdditionalFilesChange = (e) => {
    const files = Array.from(e.target.files);
    setFormData({ ...formData, additionalFiles: files });
  };

  return (
    <div className="p-4 space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">3D Models</h1>
          <p className="text-sm text-gray-500">Upload and manage 3D models for capacity planning</p>
        </div>
        <div className="flex gap-2">
          <Link to="/" className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">
            ← Dashboard
          </Link>
          {!showForm && (
            <button
              onClick={() => setShowForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              + Upload Model
            </button>
          )}
        </div>
      </header>

      {showForm && (
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Upload 3D Model</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Project *</label>
              <select
                required
                className="w-full border rounded p-2"
                value={formData.project_id}
                onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
              >
                <option value="">Select a project</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Model Name *</label>
              <input
                type="text"
                required
                className="w-full border rounded p-2"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Boeing 747 Assembly"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">3D Model File *</label>
              <input
                type="file"
                required
                accept=".obj,.gltf,.glb,.stl,.ply,.dae"
                className="w-full border rounded p-2"
                onChange={handleFileChange}
              />
              <p className="text-xs text-gray-500 mt-1">
                Supported formats: OBJ, GLTF, GLB, STL, PLY, DAE. The system will automatically generate a shape-aware grid.
                <strong>Note:</strong> Convert FBX files to OBJ/GLTF using Blender first.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Additional Files (optional)</label>
              <input
                type="file"
                multiple
                accept=".bin,.png,.jpg,.jpeg"
                className="w-full border rounded p-2"
                onChange={handleAdditionalFilesChange}
              />
              <p className="text-xs text-gray-500 mt-1">
                For GLTF models: upload associated .bin files and textures here. All files will be kept together.
              </p>
              {formData.additionalFiles.length > 0 && (
                <p className="text-xs text-blue-600 mt-1">
                  {formData.additionalFiles.length} file(s) selected: {formData.additionalFiles.map(f => f.name).join(", ")}
                </p>
              )}
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={uploading}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
              >
                {uploading ? "Uploading..." : "Upload & Generate Grid"}
              </button>
              <button
                type="button"
                onClick={resetForm}
                disabled={uploading}
                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400 disabled:bg-gray-200"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-4">
        {models.length === 0 && !showForm && (
          <div className="bg-white rounded-2xl shadow p-8 text-center">
            <p className="text-gray-500 mb-4">No 3D models yet. Upload your first model to get started!</p>
            <button
              onClick={() => setShowForm(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              + Upload First Model
            </button>
          </div>
        )}

        {models.map((model) => {
          const project = projects.find(p => p.id === model.project_id);
          return (
            <div key={model.id} className="bg-white rounded-2xl shadow p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold">{model.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Project: {project?.name || "Unknown"}
                  </p>
                  <div className="flex gap-4 mt-3 text-sm text-gray-500">
                    <span>Format: {model.format || "N/A"}</span>
                    <span>Bounds: [{model.min_x?.toFixed(1)}, {model.max_x?.toFixed(1)}] × [{model.min_y?.toFixed(1)}, {model.max_y?.toFixed(1)}] × [{model.min_z?.toFixed(1)}, {model.max_z?.toFixed(1)}]</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Link
                    to={`/model/${model.id}`}
                    className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
                  >
                    View Grid
                  </Link>
                  <button
                    onClick={() => handleDelete(model.id)}
                    className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
