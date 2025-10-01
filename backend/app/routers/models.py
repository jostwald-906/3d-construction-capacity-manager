from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, require_role
from app.models.entities import Model, Project
from app.schemas.schemas import ModelCreate, ModelOut
from app.services.ifc_revit_adapter import parse_bounds_from_file

router = APIRouter()

@router.post("", response_model=ModelOut, dependencies=[Depends(require_role("admin"))])
def create_model(payload: ModelCreate, db: Session = Depends(get_db)):
    proj = db.query(Project).get(payload.project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    bounds = parse_bounds_from_file(payload.model_file_path, payload.format)
    m = Model(
        project_id=payload.project_id,
        name=payload.name,
        format=payload.format,
        model_file_path=payload.model_file_path,
        min_x=payload.min_x if payload.min_x is not None else bounds.min_x,
        max_x=payload.max_x if payload.max_x is not None else bounds.max_x,
        min_y=payload.min_y if payload.min_y is not None else bounds.min_y,
        max_y=payload.max_y if payload.max_y is not None else bounds.max_y,
        min_z=payload.min_z if payload.min_z is not None else bounds.min_z,
        max_z=payload.max_z if payload.max_z is not None else bounds.max_z,
    )
    db.add(m); db.commit(); db.refresh(m)
    return ModelOut(**{
        "id": m.id, "project_id": m.project_id, "name": m.name, "format": m.format,
        "model_file_path": m.model_file_path, "min_x": m.min_x, "max_x": m.max_x,
        "min_y": m.min_y, "max_y": m.max_y, "min_z": m.min_z, "max_z": m.max_z
    })

@router.get("", response_model=list[ModelOut])
def list_models(db: Session = Depends(get_db)):
    ms = db.query(Model).all()
    return [ModelOut(**{
        "id": m.id, "project_id": m.project_id, "name": m.name, "format": m.format,
        "model_file_path": m.model_file_path, "min_x": m.min_x, "max_x": m.max_x,
        "min_y": m.min_y, "max_y": m.max_y, "min_z": m.min_z, "max_z": m.max_z
    }) for m in ms]
