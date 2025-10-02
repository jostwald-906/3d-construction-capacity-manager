from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, require_role
from app.models.entities import Project
from app.schemas.schemas import ProjectCreate, ProjectOut

router = APIRouter()

@router.post("", response_model=ProjectOut, dependencies=[Depends(require_role("admin"))])
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    p = Project(**payload.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return ProjectOut(**payload.model_dump(), id=p.id)

@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    projs = db.query(Project).all()
    return [ProjectOut(id=p.id, name=p.name, description=p.description, start_date=p.start_date, end_date=p.end_date) for p in projs]

@router.put("/{project_id}", response_model=ProjectOut, dependencies=[Depends(require_role("admin"))])
def update_project(project_id: int, payload: ProjectCreate, db: Session = Depends(get_db)):
    p = db.query(Project).get(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in payload.model_dump().items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return ProjectOut(id=p.id, name=p.name, description=p.description, start_date=p.start_date, end_date=p.end_date)

@router.delete("/{project_id}", response_model=dict, dependencies=[Depends(require_role("admin"))])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).get(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(p)
    db.commit()
    return {"deleted": project_id}
