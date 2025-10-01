from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.models.base import Base
from datetime import date

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    start_date: Mapped[date | None]
    end_date: Mapped[date | None]
    models = relationship("Model", back_populates="project", cascade="all, delete-orphan")

class Model(Base):
    __tablename__ = "models"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str]
    format: Mapped[str | None]
    model_file_path: Mapped[str | None]
    min_x: Mapped[float] = mapped_column(default=0.0)
    max_x: Mapped[float] = mapped_column(default=100.0)
    min_y: Mapped[float] = mapped_column(default=0.0)
    max_y: Mapped[float] = mapped_column(default=20.0)
    min_z: Mapped[float] = mapped_column(default=0.0)
    max_z: Mapped[float] = mapped_column(default=20.0)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    project = relationship("Project", back_populates="models")
    grid_cells = relationship("GridCell", back_populates="model", cascade="all, delete-orphan")

class GridCell(Base):
    __tablename__ = "grid_cells"
    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))
    x_index: Mapped[int]
    y_index: Mapped[int]
    z_index: Mapped[int]
    min_x: Mapped[float]
    max_x: Mapped[float]
    min_y: Mapped[float]
    max_y: Mapped[float]
    min_z: Mapped[float]
    max_z: Mapped[float]
    total_capacity: Mapped[int]
    footprint = Column(Geometry(geometry_type="POLYGON", srid=3857))
    model = relationship("Model", back_populates="grid_cells")
    trade_caps = relationship("TradeCapacity", back_populates="grid_cell", cascade="all, delete-orphan")
    allocations = relationship("Allocation", back_populates="grid_cell", cascade="all, delete-orphan")

class Trade(Base):
    __tablename__ = "trades"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    trade_caps = relationship("TradeCapacity", back_populates="trade", cascade="all, delete-orphan")
    allocations = relationship("Allocation", back_populates="trade", cascade="all, delete-orphan")

class TradeCapacity(Base):
    __tablename__ = "trade_capacities"
    id: Mapped[int] = mapped_column(primary_key=True)
    gridcell_id: Mapped[int] = mapped_column(ForeignKey("grid_cells.id"))
    trade_id: Mapped[int] = mapped_column(ForeignKey("trades.id"))
    max_workers: Mapped[int]
    grid_cell = relationship("GridCell", back_populates="trade_caps")
    trade = relationship("Trade", back_populates="trade_caps")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(CheckConstraint("role in ('admin','trade_manager','viewer')"))
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    allocations = relationship("Allocation", back_populates="creator")

class Allocation(Base):
    __tablename__ = "allocations"
    id: Mapped[int] = mapped_column(primary_key=True)
    gridcell_id: Mapped[int] = mapped_column(ForeignKey("grid_cells.id"))
    trade_id: Mapped[int] = mapped_column(ForeignKey("trades.id"))
    work_date: Mapped[date]
    end_date: Mapped[date | None]
    num_workers: Mapped[int | None]
    description: Mapped[str | None]
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    grid_cell = relationship("GridCell", back_populates="allocations")
    trade = relationship("Trade", back_populates="allocations")
    creator = relationship("User", back_populates="allocations")
