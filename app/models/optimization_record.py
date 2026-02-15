from sqlalchemy import Column, Integer, Float, JSON
from app.core.database import Base


class OptimizationRecord(Base):
    __tablename__ = "optimizations"

    id = Column(Integer, primary_key=True, index=True)
    total_distance = Column(Float)
    assignments = Column(JSON)