from ortools.linear_solver import pywraplp
from app.models.delivery import (
    OptimizationRequest,
    OptimizationResponse,
    AssignedDelivery
)
from fastapi import HTTPException
from app.core.database import SessionLocal
from app.models.optimization_record import OptimizationRecord
from sqlalchemy.exc import SQLAlchemyError


def _create_solver() -> pywraplp.Solver:
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        raise HTTPException(status_code=500, detail="Unable to initialize solver")
    return solver


def _create_assignment_variables(
    solver: pywraplp.Solver,
    deliveries_count: int,
    vehicle_count: int
) -> dict[tuple[int, int], pywraplp.Variable]:
    x = {}
    for delivery_index in range(deliveries_count):
        for vehicle_index in range(vehicle_count):
            x[delivery_index, vehicle_index] = solver.IntVar(
                0,
                1,
                f"x_{delivery_index}_{vehicle_index}"
            )
    return x


def _add_constraints(
    solver: pywraplp.Solver,
    x: dict[tuple[int, int], pywraplp.Variable],
    request: OptimizationRequest
) -> None:
    deliveries = request.deliveries
    vehicle_count = request.number_of_vehicles

    for delivery_index in range(len(deliveries)):
        solver.Add(sum(x[delivery_index, v] for v in range(vehicle_count)) == 1)

    for vehicle_index in range(vehicle_count):
        solver.Add(
            sum(
                x[delivery_index, vehicle_index] * deliveries[delivery_index].distance_km
                for delivery_index in range(len(deliveries))
            ) <= request.max_distance_per_vehicle
        )


def _set_objective(
    solver: pywraplp.Solver,
    x: dict[tuple[int, int], pywraplp.Variable],
    request: OptimizationRequest
) -> None:
    objective = solver.Objective()
    for delivery_index, delivery in enumerate(request.deliveries):
        for vehicle_index in range(request.number_of_vehicles):
            cost = delivery.distance_km * (6 - delivery.priority)
            objective.SetCoefficient(x[delivery_index, vehicle_index], cost)

    objective.SetMinimization()


def _extract_assignments(
    x: dict[tuple[int, int], pywraplp.Variable],
    request: OptimizationRequest
) -> tuple[list[AssignedDelivery], float]:
    assignments: list[AssignedDelivery] = []
    total_distance = 0.0

    for delivery_index, delivery in enumerate(request.deliveries):
        for vehicle_index in range(request.number_of_vehicles):
            if x[delivery_index, vehicle_index].solution_value() == 1:
                assignments.append(
                    AssignedDelivery(
                        delivery_id=delivery.id,
                        vehicle_id=vehicle_index
                    )
                )
                total_distance += delivery.distance_km

    return assignments, total_distance


def _persist_optimization(assignments: list[AssignedDelivery], total_distance: float) -> None:
    db = SessionLocal()
    try:
        record = OptimizationRecord(
            total_distance=total_distance,
            assignments=[assignment.model_dump() for assignment in assignments]
        )
        db.add(record)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to persist optimization results: {e}"
        )
    finally:
        db.close()


def optimize_deliveries(request: OptimizationRequest) -> OptimizationResponse:
    solver = _create_solver()

    deliveries = request.deliveries
    num_vehicles = request.number_of_vehicles

    x = _create_assignment_variables(solver, len(deliveries), num_vehicles)
    _add_constraints(solver, x, request)
    _set_objective(solver, x, request)

    status = solver.Solve()

    if status != pywraplp.Solver.OPTIMAL:
        raise HTTPException(
            status_code=400,
            detail="No feasible solution found with given constraints"
        )

    assignments, total_distance = _extract_assignments(x, request)
    _persist_optimization(assignments, total_distance)

    return OptimizationResponse(
        total_distance=total_distance,
        assignments=assignments
    )