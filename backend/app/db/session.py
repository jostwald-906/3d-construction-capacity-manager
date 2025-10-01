from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

engine = create_engine(settings.db_url(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
