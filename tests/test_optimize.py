from fastapi.testclient import TestClient
import pytest
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_optimize_success(client):
    payload = {
        "deliveries": [
            {"id": 1, "distance_km": 10, "priority": 3, "deadline_hour": 12},
            {"id": 2, "distance_km": 5, "priority": 5, "deadline_hour": 10}
        ],
        "number_of_vehicles": 2,
        "max_distance_per_vehicle": 20
    }

    response = client.post("/optimize", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["total_distance"] == 15
    assert len(data["assignments"]) == 2


def test_optimize_infeasible(client):
    payload = {
        "deliveries": [
            {"id": 1, "distance_km": 10, "priority": 3, "deadline_hour": 12},
            {"id": 2, "distance_km": 5, "priority": 5, "deadline_hour": 10}
        ],
        "number_of_vehicles": 1,
        "max_distance_per_vehicle": 12
    }

    response = client.post("/optimize", json=payload)

    assert response.status_code == 400