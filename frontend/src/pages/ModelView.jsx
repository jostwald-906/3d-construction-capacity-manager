import React, { useEffect, useRef, useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import client from "../api/client.js";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

function ThreeGrid({ cells, overSet }) {
  const mountRef = useRef(null);
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

    cells.forEach(c => {
      const w = (c.max_x - c.min_x);
      const h = (c.max_y - c.min_y);
      const d = (c.max_z - c.min_z);
      const box = new THREE.BoxGeometry(w, h, d);
      const mat = overSet.has(c.id) ? over : normal;
      const mesh = new THREE.Mesh(box, mat);
      mesh.position.set((c.min_x + c.max_x)/2, (c.min_y + c.max_y)/2, (c.min_z + c.max_z)/2);
      group.add(mesh);
    });
    scene.add(group);

    const controls = new OrbitControls(camera, renderer.domElement);

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

  const overSet = useMemo(() => {
    const map = new Map();
    cells.forEach(c => map.set(c.id, { total: c.total_capacity, used: 0, byTrade: {} }));
    allocs.forEach(a => {
      const entry = map.get(a.gridcell_id);
      if (!entry) return;
      const w = a.num_workers ?? 1;
      entry.used += w;
      entry.byTrade[a.trade_id] = (entry.byTrade[a.trade_id] || 0) + w;
    });
    const overs = new Set();
    cells.forEach(c => {
      const e = map.get(c.id);
      if (!e) return;
      if (e.used > c.total_capacity) overs.add(c.id);
    });
    return overs;
  }, [cells, allocs, tradeId, trades]);

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

  return (
    <div className="p-4 space-y-4">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 space-y-2">
          <div className="bg-white rounded-2xl shadow p-4">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold">{model?.name || "Model"}</h1>
              <div className="text-sm text-gray-500">Bounds: [{model?.min_x},{model?.max_x}]×[{model?.min_y},{model?.max_y}]×[{model?.min_z},{model?.max_z}]</div>
            </div>
            <div className="mt-2 grid grid-cols-2 md:grid-cols-6 gap-2">
              <input className="border rounded p-2" type="number" value={sections.x} onChange={e=>setSections(s=>({...s,x:e.target.value}))} placeholder="X sections" />
              <input className="border rounded p-2" type="number" value={sections.y} onChange={e=>setSections(s=>({...s,y:e.target.value}))} placeholder="Y sections" />
              <input className="border rounded p-2" type="number" value={sections.z} onChange={e=>setSections(s=>({...s,z:e.target.value}))} placeholder="Z sections" />
              <input className="border rounded p-2" type="number" value={sections.cap} onChange={e=>setSections(s=>({...s,cap:e.target.value}))} placeholder="Default capacity" />
              <button onClick={regen} className="bg-blue-600 text-white rounded p-2">Regenerate Grid</button>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow p-4">
            <div className="grid md:grid-cols-4 gap-2">
              <input className="border rounded p-2" type="date" value={date} onChange={e=>setDate(e.target.value)} />
              <select className="border rounded p-2" value={tradeId} onChange={e=>setTradeId(e.target.value)}>
                <option value="">All trades</option>
                {trades.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
          </div>

          <ThreeGrid cells={cells} overSet={overSet} />
        </div>

        <div className="w-full md:w-80 bg-white rounded-2xl shadow p-4 h-fit">
          <h2 className="font-semibold mb-2">Allocations ({allocs.length})</h2>
          <div className="space-y-2 max-h-[60vh] overflow-auto">
            {allocs.map(a => (
              <div key={a.id} className="border rounded-lg p-2">
                <div className="text-sm">Cell #{a.gridcell_id} • Trade {a.trade_id}</div>
                <div className="text-xs text-gray-500">{a.work_date}{a.end_date ? ` → ${a.end_date}` : ""}</div>
                <div className="text-xs">Workers: {a.num_workers ?? 1}</div>
              </div>
            ))}
            {!allocs.length && <div className="text-sm text-gray-500">No allocations on selected date.</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
