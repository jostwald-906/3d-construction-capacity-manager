import datetime
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.entities import Project, Model, GridCell, Trade, Allocation, TradeCapacity
from app.services.grid_service import generate_grid, capacity_check

def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)

def test_grid_generation_and_capacity():
    db = SessionLocal()
    try:
        p = Project(name="Test", description=None, start_date=None, end_date=None)
        db.add(p); db.commit(); db.refresh(p)
        m = Model(project_id=p.id, name="Mock Sub", format="mock", model_file_path=None,
                  min_x=0, max_x=10, min_y=0, max_y=10, min_z=0, max_z=10)
        db.add(m); db.commit(); db.refresh(m)

        cells = generate_grid(db, m, 2, 2, 2, 5)
        assert len(cells) == 8
        c0 = cells[0]
        assert c0.total_capacity == 5

        t = Trade(name="Electrical")
        db.add(t); db.commit(); db.refresh(t)

        ok, reason = capacity_check(db, c0.id, t.id, datetime.date(2025,1,1), datetime.date(2025,1,1), 3)
        assert ok

        a = Allocation(gridcell_id=c0.id, trade_id=t.id, work_date=datetime.date(2025,1,1), num_workers=3)
        db.add(a); db.commit()

        ok, reason = capacity_check(db, c0.id, t.id, datetime.date(2025,1,1), datetime.date(2025,1,1), 3)
        assert not ok and reason == "Total capacity exceeded"

        tc = TradeCapacity(gridcell_id=c0.id, trade_id=t.id, max_workers=2)
        db.add(tc); db.commit()
        ok, reason = capacity_check(db, c0.id, t.id, datetime.date(2025,1,2), datetime.date(2025,1,2), 3)
        assert not ok and reason == "Trade capacity exceeded"
    finally:
        db.close()
