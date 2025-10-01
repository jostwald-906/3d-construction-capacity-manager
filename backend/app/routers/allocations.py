from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user, require_role
from app.models.entities import Allocation
from app.schemas.schemas import AllocationCreate, AllocationOut
from app.services.grid_service import capacity_check

router = APIRouter()

@router.post("", response_model=AllocationOut, dependencies=[Depends(require_role("admin","trade_manager"))])
def create_allocation(payload: AllocationCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    start = payload.work_date
    end = payload.end_date or payload.work_date
    new_workers = payload.num_workers or 1
    ok, reason = capacity_check(db, payload.gridcell_id, payload.trade_id, start, end, new_workers)
    if not ok:
        raise HTTPException(status_code=400, detail=reason)
    a = Allocation(**payload.model_dump(), created_by=user.id)
    db.add(a); db.commit(); db.refresh(a)
    return AllocationOut(**payload.model_dump(), id=a.id, created_by=user.id)

@router.get("/by-date/{work_date}", response_model=list[AllocationOut])
def list_by_date(work_date: date, db: Session = Depends(get_db)):
    allocs = db.query(Allocation).filter(Allocation.work_date <= work_date, (Allocation.end_date == None) | (Allocation.end_date >= work_date)).all()
    return [AllocationOut(
        id=a.id, gridcell_id=a.gridcell_id, trade_id=a.trade_id, work_date=a.work_date, end_date=a.end_date,
        num_workers=a.num_workers, description=a.description, created_by=a.created_by
    ) for a in allocs]

@router.delete("/{allocation_id}", response_model=dict, dependencies=[Depends(require_role("admin","trade_manager"))])
def delete_allocation(allocation_id: int, db: Session = Depends(get_db)):
    a = db.query(Allocation).get(allocation_id)
    if not a:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(a); db.commit()
    return {"deleted": allocation_id}
