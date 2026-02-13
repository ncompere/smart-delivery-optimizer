from ortools.linear_solver import pywraplp
from app.models.delivery import (
    OptimizationRequest,
    OptimizationResponse,
    AssignedDelivery
)
from fastapi import HTTPException


def optimize_deliveries(request: OptimizationRequest) -> OptimizationResponse:
    solver = pywraplp.Solver.CreateSolver("SCIP")

    deliveries = request.deliveries
    num_vehicles = request.number_of_vehicles

    # Variables x[d][v] = 1 si delivery d assignée au véhicule v
    x = {}
    for d_idx, delivery in enumerate(deliveries):
        for v in range(num_vehicles):
            x[d_idx, v] = solver.IntVar(0, 1, f"x_{d_idx}_{v}")

    # Chaque livraison doit être assignée à un seul véhicule
    for d_idx in range(len(deliveries)):
        solver.Add(sum(x[d_idx, v] for v in range(num_vehicles)) == 1)

        # Contrainte de distance maximale par véhicule
    for v in range(num_vehicles):
        solver.Add(
            sum(
                x[d_idx, v] * deliveries[d_idx].distance_km
                for d_idx in range(len(deliveries))
            ) <= request.max_distance_per_vehicle
        )

    # Fonction objectif : minimiser distance pondérée par priorité
    objective = solver.Objective()
    for d_idx, delivery in enumerate(deliveries):
        for v in range(num_vehicles):
            cost = delivery.distance_km * (6 - delivery.priority)
            objective.SetCoefficient(x[d_idx, v], cost)

    objective.SetMinimization()

    status = solver.Solve()

    if status != pywraplp.Solver.OPTIMAL:
        raise HTTPException(
            status_code=400,
            detail="No feasible solution found with given constraints"
        )

    assignments = []
    total_distance = 0

    for d_idx, delivery in enumerate(deliveries):
        for v in range(num_vehicles):
            if x[d_idx, v].solution_value() == 1:
                assignments.append(
                    AssignedDelivery(
                        delivery_id=delivery.id,
                        vehicle_id=v
                    )
                )
                total_distance += delivery.distance_km

    return OptimizationResponse(
        total_distance=total_distance,
        assignments=assignments
    )