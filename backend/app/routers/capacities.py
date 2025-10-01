from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, require_role
from app.models.entities import GridCell, TradeCapacity
from app.schemas.schemas import TradeCapacityCreate, TradeCapacityOut, CellCapacityUpdate

router = APIRouter()

@router.patch("/cell/{cell_id}", response_model=dict, dependencies=[Depends(require_role("admin"))])
def update_cell_capacity(cell_id: int, payload: CellCapacityUpdate, db: Session = Depends(get_db)):
    c = db.query(GridCell).get(cell_id)
    if not c:
        raise HTTPException(status_code=404, detail="Cell not found")
    c.total_capacity = payload.total_capacity
    db.commit()
    return {"id": c.id, "total_capacity": c.total_capacity}

@router.post("/trade", response_model=TradeCapacityOut, dependencies=[Depends(require_role("admin"))])
def upsert_trade_capacity(payload: TradeCapacityCreate, db: Session = Depends(get_db)):
    tc = db.query(TradeCapacity).filter(
        TradeCapacity.gridcell_id == payload.gridcell_id, TradeCapacity.trade_id == payload.trade_id
    ).first()
    if tc:
        tc.max_workers = payload.max_workers
        db.commit(); db.refresh(tc)
        return TradeCapacityOut(id=tc.id, gridcell_id=tc.gridcell_id, trade_id=tc.trade_id, max_workers=tc.max_workers)
    tc = TradeCapacity(**payload.model_dump())
    db.add(tc); db.commit(); db.refresh(tc)
    return TradeCapacityOut(id=tc.id, gridcell_id=tc.gridcell_id, trade_id=tc.trade_id, max_workers=tc.max_workers)
