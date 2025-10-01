from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, require_role
from app.models.entities import Trade
from app.schemas.schemas import TradeCreate, TradeOut

router = APIRouter()

@router.post("", response_model=TradeOut, dependencies=[Depends(require_role("admin"))])
def create_trade(payload: TradeCreate, db: Session = Depends(get_db)):
    if db.query(Trade).filter(Trade.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Trade exists")
    t = Trade(name=payload.name)
    db.add(t); db.commit(); db.refresh(t)
    return TradeOut(id=t.id, name=t.name)

@router.get("", response_model=list[TradeOut])
def list_trades(db: Session = Depends(get_db)):
    ts = db.query(Trade).all()
    return [TradeOut(id=t.id, name=t.name) for t in ts]
