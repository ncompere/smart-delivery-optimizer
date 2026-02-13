from fastapi import FastAPI
from app.models.delivery import OptimizationRequest, OptimizationResponse
from app.services.optimizer import optimize_deliveries

app = FastAPI(title="Smart Delivery Optimizer API")


@app.get("/")
def health_check():
    return {"status": "API is running"}


@app.post("/optimize", response_model=OptimizationResponse)
def optimize(request: OptimizationRequest):
    return optimize_deliveries(request)