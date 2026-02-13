from pydantic import BaseModel, Field
from typing import List


class Delivery(BaseModel):
    id: int
    distance_km: float = Field(..., gt=0)
    priority: int = Field(..., ge=1, le=5)
    deadline_hour: int = Field(..., ge=0, le=24)


class OptimizationRequest(BaseModel):
    deliveries: List[Delivery]
    number_of_vehicles: int = Field(..., gt=0)
    max_distance_per_vehicle: float = Field(..., gt=0)


class AssignedDelivery(BaseModel):
    delivery_id: int
    vehicle_id: int


class OptimizationResponse(BaseModel):
    total_distance: float
    assignments: List[AssignedDelivery]