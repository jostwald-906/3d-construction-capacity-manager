export function usageByXY(cells, allocations, mode = "aggregate") {
  const key = (x,y)=>`${x},${y}`;
  const byKey = new Map();
  cells.forEach(c => {
    const k = key(c.x_index, c.y_index);
    if (!byKey.has(k)) byKey.set(k, { cap: 0, use: 0 });
    const v = byKey.get(k);
    v.cap += c.total_capacity;
  });
  allocations.forEach(a => {
    const c = cells.find(cc => cc.id === a.gridcell_id);
    if (!c) return;
    const k = key(c.x_index, c.y_index);
    const v = byKey.get(k);
    if (!v) return;
    v.use += (a.num_workers ?? 1);
  });
  return Array.from(byKey.entries()).map(([k,v]) => {
    const [x,y] = k.split(",").map(Number);
    return { x, y, usage: v.cap ? v.use / v.cap : 0 };
  });
}
