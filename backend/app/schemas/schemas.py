from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserOut(UserBase):
    id: int

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ProjectOut(ProjectCreate):
    id: int

class ModelCreate(BaseModel):
    project_id: int
    name: str
    format: str | None = None
    model_file_path: str | None = None
    min_x: float | None = None
    max_x: float | None = None
    min_y: float | None = None
    max_y: float | None = None
    min_z: float | None = None
    max_z: float | None = None

class ModelOut(ModelCreate):
    id: int

class GridGenRequest(BaseModel):
    model_id: int
    sections_x: int
    sections_y: int
    sections_z: int
    default_capacity: int = 10

    @field_validator("sections_x","sections_y","sections_z")
    @classmethod
    def positive(cls, v):
        if v <= 0:
            raise ValueError("sections must be > 0")
        return v

class GridCellOut(BaseModel):
    id: int
    model_id: int
    x_index: int
    y_index: int
    z_index: int
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float
    total_capacity: int

class TradeCreate(BaseModel):
    name: str

class TradeOut(BaseModel):
    id: int
    name: str

class TradeCapacityCreate(BaseModel):
    gridcell_id: int
    trade_id: int
    max_workers: int

class TradeCapacityOut(TradeCapacityCreate):
    id: int

class CellCapacityUpdate(BaseModel):
    total_capacity: int

class AllocationCreate(BaseModel):
    gridcell_id: int
    trade_id: int
    work_date: date
    end_date: date | None = None
    num_workers: int | None = None
    description: str | None = None

class AllocationOut(AllocationCreate):
    id: int
    created_by: int | None = None
