import { describe, it, expect } from "vitest";
import { usageByXY } from "../utils/heatmap.js";

describe("usageByXY", () => {
  it("computes utilization by XY", () => {
    const cells = [
      {id:1,x_index:0,y_index:0,total_capacity:5},
      {id:2,x_index:0,y_index:0,total_capacity:5},
      {id:3,x_index:1,y_index:0,total_capacity:10}
    ];
    const allocations = [
      {gridcell_id:1,num_workers:3},
      {gridcell_id:3,num_workers:5}
    ];
    const res = usageByXY(cells, allocations);
    const a00 = res.find(r => r.x===0 && r.y===0);
    const a10 = res.find(r => r.x===1 && r.y===0);
    expect(a00.usage).toBeCloseTo(3/10);
    expect(a10.usage).toBeCloseTo(5/10);
  });
});
