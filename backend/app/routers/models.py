from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.deps import get_db, require_role
from app.models.entities import Model, Project
from app.schemas.schemas import ModelCreate, ModelOut
from app.services.ifc_revit_adapter import parse_bounds_from_file
from app.services.model_parser import parse_3d_model
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

@router.post("/upload", response_model=ModelOut, dependencies=[Depends(require_role("admin"))])
async def upload_model(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    name: str = Form(...),
    additional_files: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    proj = db.query(Project).get(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validate file extension
    ext = file.filename.split('.')[-1].lower()
    supported_formats = ['obj', 'gltf', 'glb', 'stl', 'ply', 'dae']
    if ext not in supported_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Supported: {', '.join(supported_formats)}. Note: FBX files should be converted to OBJ or GLTF using Blender or Autodesk FBX Converter.")

    # Create unique directory for this model to store all associated files
    model_id = str(uuid.uuid4())
    model_dir = os.path.join(UPLOAD_DIR, model_id)
    os.makedirs(model_dir, exist_ok=True)

    # Save main file
    main_filename = file.filename
    file_path = os.path.join(model_dir, main_filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Save additional files (for GLTF .bin files, textures, etc.)
    for additional_file in additional_files:
        if additional_file.filename:
            additional_path = os.path.join(model_dir, additional_file.filename)
            with open(additional_path, "wb") as f:
                content = await additional_file.read()
                f.write(content)

    # Parse 3D model to get bounds
    try:
        bounds = parse_3d_model(file_path, ext)
    except Exception as e:
        # Clean up on error
        import shutil
        shutil.rmtree(model_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Failed to parse 3D model: {str(e)}")

    # Create model record
    m = Model(
        project_id=project_id,
        name=name,
        format=ext,
        model_file_path=file_path,
        min_x=bounds['min_x'],
        max_x=bounds['max_x'],
        min_y=bounds['min_y'],
        max_y=bounds['max_y'],
        min_z=bounds['min_z'],
        max_z=bounds['max_z'],
    )
    db.add(m)
    db.commit()
    db.refresh(m)

    return ModelOut(**{
        "id": m.id, "project_id": m.project_id, "name": m.name, "format": m.format,
        "model_file_path": m.model_file_path, "min_x": m.min_x, "max_x": m.max_x,
        "min_y": m.min_y, "max_y": m.max_y, "min_z": m.min_z, "max_z": m.max_z
    })

@router.delete("/{model_id}", response_model=dict, dependencies=[Depends(require_role("admin"))])
def delete_model(model_id: int, db: Session = Depends(get_db)):
    import shutil
    m = db.query(Model).get(model_id)
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")

    # Delete file/directory if exists
    if m.model_file_path and os.path.exists(m.model_file_path):
        # Check if it's in a dedicated directory (new multi-file structure)
        model_dir = os.path.dirname(m.model_file_path)
        if model_dir != UPLOAD_DIR and os.path.exists(model_dir):
            # Remove entire directory with all associated files
            shutil.rmtree(model_dir, ignore_errors=True)
        else:
            # Remove single file (old structure)
            os.remove(m.model_file_path)

    db.delete(m)
    db.commit()
    return {"deleted": model_id}
