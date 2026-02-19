# Smart Delivery Optimizer

FastAPI API for optimizing the assignment of deliveries to vehicles using OR-Tools.

## Prerequisites

- Python 3.11
- Poetry

## Installation

```bash
poetry install
```

## Running the API

```bash
poetry run uvicorn app.main:app --reload
```

Main endpoints:

- `GET /` : healthcheck
- `POST /optimize` : computes a delivery assignment

## Running the tests

```bash
poetry run pytest -q
```

## Configuration

The following environment variable is supported:

- `DATABASE_URL`

Default behavior:

- if `DATABASE_URL` is not set, the application uses a local SQLite database (`sqlite:///./delivery_optimizer.db`)
- for PostgreSQL, set for example:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/delivery_optimizer"
```

## Project structure

```text
app/
    main.py                 # FastAPI entry point
    core/database.py        # SQLAlchemy configuration
    models/                 # Pydantic schemas + SQLAlchemy model
    services/optimizer.py   # OR-Tools optimization logic
tests/
    test_optimize.py        # API tests
```
