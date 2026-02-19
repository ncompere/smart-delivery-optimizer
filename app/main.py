from fastapi import FastAPI
from app.models.delivery import OptimizationRequest, OptimizationResponse
from app.services.optimizer import optimize_deliveries
from app.core.database import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    yield
    # Shutdown logic (if needed) goes here


app = FastAPI(title="Smart Delivery Optimizer API", lifespan=lifespan)
@app.get("/")
def health_check():
    return {"status": "API is running"}


@app.post("/optimize", response_model=OptimizationResponse)
def optimize(request: OptimizationRequest):
    return optimize_deliveries(request)