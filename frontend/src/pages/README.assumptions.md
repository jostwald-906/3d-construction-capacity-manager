# Frontend Assumptions

- Three.js scene uses simple Meshes for clarity. For >2k cells, switch to InstancedMesh.
- No file upload UI yet; models are created via API using mock bounds.
- Heatmap is not rendered here; `usageByXY` utility is provided for future D3 layer.
- OrbitControls imported using ESM syntax for Vite compatibility.
