from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, require_role
from app.models.entities import Model, GridCell
from app.schemas.schemas import GridGenRequest, GridCellOut
from app.services.grid_service import generate_grid

router = APIRouter()

@router.post("/generate", response_model=list[GridCellOut], dependencies=[Depends(require_role("admin"))])
def generate(payload: GridGenRequest, db: Session = Depends(get_db)):
    m = db.query(Model).get(payload.model_id)
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")
    cells = generate_grid(db, m, payload.sections_x, payload.sections_y, payload.sections_z, payload.default_capacity)
    return [
        GridCellOut(
            id=c.id, model_id=c.model_id, x_index=c.x_index, y_index=c.y_index, z_index=c.z_index,
            min_x=c.min_x, max_x=c.max_x, min_y=c.min_y, max_y=c.max_y, min_z=c.min_z, max_z=c.max_z,
            total_capacity=c.total_capacity
        ) for c in cells
    ]

@router.get("/{model_id}", response_model=list[GridCellOut])
def list_cells(model_id: int, db: Session = Depends(get_db)):
    cells = db.query(GridCell).filter(GridCell.model_id == model_id).all()
    return [
        GridCellOut(
            id=c.id, model_id=c.model_id, x_index=c.x_index, y_index=c.y_index, z_index=c.z_index,
            min_x=c.min_x, max_x=c.max_x, min_y=c.min_y, max_y=c.max_y, min_z=c.min_z, max_z=c.max_z,
            total_capacity=c.total_capacity
        ) for c in cells
    ]
