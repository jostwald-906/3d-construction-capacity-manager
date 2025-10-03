from typing import List, Tuple
from shapely.geometry import Polygon
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from geoalchemy2.shape import from_shape
from app.models.entities import Model, GridCell, Allocation, TradeCapacity
from app.services.model_parser import parse_3d_model
import os

def generate_grid(db: Session, model: Model, sx: int, sy: int, sz: int, default_capacity: int) -> List[GridCell]:
    db.query(GridCell).filter(GridCell.model_id == model.id).delete()
    dx = (model.max_x - model.min_x) / sx
    dy = (model.max_y - model.min_y) / sy
    dz = (model.max_z - model.min_z) / sz

    # Load model geometry if available for shape-aware voxelization
    vertices = None
    if model.model_file_path and os.path.exists(model.model_file_path):
        try:
            parsed = parse_3d_model(model.model_file_path, model.format)
            vertices = parsed.get('vertices', None)
        except:
            pass  # Fall back to bounding box grid if parsing fails

    cells: List[GridCell] = []
    for i in range(sx):
        for j in range(sy):
            for k in range(sz):
                min_x = model.min_x + i * dx
                max_x = min_x + dx
                min_y = model.min_y + j * dy
                max_y = min_y + dy
                min_z = model.min_z + k * dz
                max_z = min_z + dz

                # Shape-aware filtering: only create cell if it contains geometry
                if vertices:
                    cell_contains_geometry = any(
                        min_x <= v[0] <= max_x and
                        min_y <= v[1] <= max_y and
                        min_z <= v[2] <= max_z
                        for v in vertices
                    )
                    if not cell_contains_geometry:
                        continue  # Skip empty cells

                poly = Polygon([(min_x, min_y),(max_x, min_y),(max_x, max_y),(min_x, max_y)])
                cell = GridCell(
                    model_id=model.id,
                    x_index=i, y_index=j, z_index=k,
                    min_x=min_x, max_x=max_x,
                    min_y=min_y, max_y=max_y,
                    min_z=min_z, max_z=max_z,
                    total_capacity=default_capacity,
                    footprint=from_shape(poly, srid=3857)
                )
                db.add(cell)
                cells.append(cell)
    db.commit()
    for c in cells:
        db.refresh(c)
    return cells

def capacity_check(db: Session, gridcell_id: int, trade_id: int, start_date, end_date, new_workers: int) -> Tuple[bool, str | None]:
    q = db.query(Allocation).filter(
        Allocation.gridcell_id == gridcell_id,
        Allocation.work_date <= end_date,
        (Allocation.end_date == None) | (Allocation.end_date >= start_date)
    )
    allocations = q.all()
    total_assigned = sum((a.num_workers or 1) for a in allocations)
    trade_assigned = sum((a.num_workers or 1) for a in allocations if a.trade_id == trade_id)

    cell = db.query(GridCell).get(gridcell_id)
    if not cell:
        return False, "Grid cell not found"
    trade_cap = db.query(TradeCapacity).filter(
        TradeCapacity.gridcell_id == gridcell_id, TradeCapacity.trade_id == trade_id
    ).first()

    if total_assigned + new_workers > cell.total_capacity:
        return True, "Warning: Total capacity exceeded"
    if trade_cap and trade_assigned + new_workers > trade_cap.max_workers:
        return True, "Warning: Trade capacity exceeded"
    return True, None
