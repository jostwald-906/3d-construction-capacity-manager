import React, { useEffect, useRef, useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import client from "../api/client.js";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

function ThreeGrid({ cells, overSet, onCellClick }) {
  const mountRef = useRef(null);
  const [raycaster] = useState(new THREE.Raycaster());
  const [mouse] = useState(new THREE.Vector2());
  const meshMapRef = useRef(new Map());

  useEffect(() => {
    const width = mountRef.current.clientWidth;
    const height = 400;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, width/height, 0.1, 5000);
    camera.position.set(0, 0, Math.max(width, height));
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1,1,1);
    scene.add(light);
    const ambient = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambient);

    const group = new THREE.Group();
    const normal = new THREE.MeshBasicMaterial({ color: 0x3399ff, transparent: true, opacity: 0.2 });
    const over = new THREE.MeshBasicMaterial({ color: 0xff3333, transparent: true, opacity: 0.5 });
    const meshMap = new Map();

    cells.forEach(c => {
      const w = (c.max_x - c.min_x);
      const h = (c.max_y - c.min_y);
      const d = (c.max_z - c.min_z);
      const box = new THREE.BoxGeometry(w, h, d);
      const mat = overSet.has(c.id) ? over : normal;
      const mesh = new THREE.Mesh(box, mat);
      mesh.position.set((c.min_x + c.max_x)/2, (c.min_y + c.max_y)/2, (c.min_z + c.max_z)/2);
      mesh.userData.cellId = c.id;
      group.add(mesh);
      meshMap.set(c.id, mesh);
    });
    scene.add(group);
    meshMapRef.current = meshMap;

    const controls = new OrbitControls(camera, renderer.domElement);

    function onClick(event) {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(group.children);
      if (intersects.length > 0) {
        const cellId = intersects[0].object.userData.cellId;
        onCellClick(cellId);
      }
    }
    renderer.domElement.addEventListener('click', onClick);

    function animate() {
      controls.update();
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }
    animate();

    function onResize() {
      const w = mountRef.current.clientWidth;
      camera.aspect = w/height;
      camera.updateProjectionMatrix();
      renderer.setSize(w, height);
    }
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      renderer.domElement.removeEventListener('click', onClick);
      mountRef.current.removeChild(renderer.domElement);
    };
  }, [cells, overSet]);

  return <div ref={mountRef} className="w-full rounded-2xl shadow bg-white" style={{height: 400}}/>;
}

export default function ModelView() {
  const { id } = useParams();
  const [model,setModel]=useState(null);
  const [cells,setCells]=useState([]);
  const [trades,setTrades]=useState([]);
  const [date,setDate]=useState(new Date().toISOString().slice(0,10));
  const [tradeId,setTradeId]=useState("");
  const [allocs,setAllocs]=useState([]);
  const [selectedCell,setSelectedCell]=useState(null);
  const [showForm,setShowForm]=useState(false);
  const [formData,setFormData]=useState({trade_id:"",num_workers:1,work_date:"",end_date:""});

  const overSet = useMemo(() => {
    const map = new Map();
    cells.forEach(c => map.set(c.id, { total: c.total_capacity, used: 0 }));
    allocs.forEach(a => {
      const entry = map.get(a.gridcell_id);
      if (entry) entry.used += (a.num_workers ?? 1);
    });
    const overs = new Set();
    cells.forEach(c => {
      const e = map.get(c.id);
      if (e && e.used > c.total_capacity) overs.add(c.id);
    });
    return overs;
  }, [cells, allocs]);

  useEffect(() => {
    (async () => {
      const m = await client.get("/models");
      const found = m.data.find(x => String(x.id) === String(id));
      setModel(found);
      if (found) {
        const cellsRes = await client.get(`/grid/${found.id}`);
        setCells(cellsRes.data);
      }
      const tradesRes = await client.get("/trades");
      setTrades(tradesRes.data);
    })();
  }, [id]);

  useEffect(() => {
    (async () => {
      const res = await client.get(`/allocations/by-date/${date}`);
      setAllocs(res.data.filter(a => cells.some(c => c.id === a.gridcell_id) && (!tradeId || a.trade_id === Number(tradeId))));
    })();
  }, [date, tradeId, cells.length]);

  const [sections, setSections] = useState({ x: 6, y: 3, z: 3, cap: 8 });

  const regen = async () => {
    if (!model) return;
    await client.post("/grid/generate", {
      model_id: model.id,
      sections_x: Number(sections.x), sections_y: Number(sections.y), sections_z: Number(sections.z),
      default_capacity: Number(sections.cap)
    });
    const cellsRes = await client.get(`/grid/${model.id}`);
    setCells(cellsRes.data);
  };

  const handleCellClick = (cellId) => {
    const cell = cells.find(c => c.id === cellId);
    setSelectedCell(cell);
    setFormData({trade_id:"",num_workers:1,work_date:date,end_date:""});
    setShowForm(true);
  };

  const createAllocation = async (e) => {
    e.preventDefault();
    if (!selectedCell || !formData.trade_id) return;
    await client.post("/allocations", {
      gridcell_id: selectedCell.id,
      trade_id: Number(formData.trade_id),
      work_date: formData.work_date,
      end_date: formData.end_date || null,
      num_workers: Number(formData.num_workers)
    });
    const res = await client.get(`/allocations/by-date/${date}`);
    setAllocs(res.data.filter(a => cells.some(c => c.id === a.gridcell_id)));
    setShowForm(false);
  };

  const deleteAllocation = async (allocId) => {
    await client.delete(`/allocations/${allocId}`);
    const res = await client.get(`/allocations/by-date/${date}`);
    setAllocs(res.data.filter(a => cells.some(c => c.id === a.gridcell_id)));
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 space-y-2">
          <div className="bg-white rounded-2xl shadow p-4">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold">{model?.name || "Model"}</h1>
              <div className="text-sm text-gray-500">Click cells to assign workers</div>
            </div>
            <div className="mt-2 grid grid-cols-2 md:grid-cols-6 gap-2">
              <input className="border rounded p-2" type="number" value={sections.x} onChange={e=>setSections(s=>({...s,x:e.target.value}))} placeholder="X" />
              <input className="border rounded p-2" type="number" value={sections.y} onChange={e=>setSections(s=>({...s,y:e.target.value}))} placeholder="Y" />
              <input className="border rounded p-2" type="number" value={sections.z} onChange={e=>setSections(s=>({...s,z:e.target.value}))} placeholder="Z" />
              <input className="border rounded p-2" type="number" value={sections.cap} onChange={e=>setSections(s=>({...s,cap:e.target.value}))} placeholder="Capacity" />
              <button onClick={regen} className="bg-blue-600 text-white rounded p-2">Regenerate Grid</button>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow p-4">
            <div className="grid md:grid-cols-3 gap-2">
              <input className="border rounded p-2" type="date" value={date} onChange={e=>setDate(e.target.value)} />
              <select className="border rounded p-2" value={tradeId} onChange={e=>setTradeId(e.target.value)}>
                <option value="">All trades</option>
                {trades.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
          </div>

          <ThreeGrid cells={cells} overSet={overSet} onCellClick={handleCellClick} />
        </div>

        <div className="w-full md:w-80 space-y-4">
          {showForm && selectedCell && (
            <div className="bg-white rounded-2xl shadow p-4">
              <h2 className="font-semibold mb-2">Assign Workers to Cell #{selectedCell.id}</h2>
              <form onSubmit={createAllocation} className="space-y-2">
                <select required className="w-full border rounded p-2" value={formData.trade_id} onChange={e=>setFormData(f=>({...f,trade_id:e.target.value}))}>
                  <option value="">Select Trade</option>
                  {trades.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
                <input required type="number" min="1" className="w-full border rounded p-2" placeholder="Workers" value={formData.num_workers} onChange={e=>setFormData(f=>({...f,num_workers:e.target.value}))} />
                <input required type="date" className="w-full border rounded p-2" value={formData.work_date} onChange={e=>setFormData(f=>({...f,work_date:e.target.value}))} />
                <input type="date" className="w-full border rounded p-2" placeholder="End date (optional)" value={formData.end_date} onChange={e=>setFormData(f=>({...f,end_date:e.target.value}))} />
                <div className="flex gap-2">
                  <button type="submit" className="flex-1 bg-green-600 text-white rounded p-2">Assign</button>
                  <button type="button" onClick={()=>setShowForm(false)} className="flex-1 bg-gray-300 rounded p-2">Cancel</button>
                </div>
              </form>
            </div>
          )}

          <div className="bg-white rounded-2xl shadow p-4">
            <h2 className="font-semibold mb-2">Allocations ({allocs.length})</h2>
            <div className="space-y-2 max-h-[60vh] overflow-auto">
              {allocs.map(a => (
                <div key={a.id} className="border rounded-lg p-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="text-sm font-medium">Cell #{a.gridcell_id} • {trades.find(t=>t.id===a.trade_id)?.name}</div>
                      <div className="text-xs text-gray-500">{a.work_date}{a.end_date ? ` → ${a.end_date}` : ""}</div>
                      <div className="text-xs">Workers: {a.num_workers ?? 1}</div>
                    </div>
                    <button onClick={()=>deleteAllocation(a.id)} className="text-red-600 text-xs px-2 py-1 border border-red-600 rounded hover:bg-red-50">Delete</button>
                  </div>
                </div>
              ))}
              {!allocs.length && <div className="text-sm text-gray-500">No allocations. Click a cell to assign workers.</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
