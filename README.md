# Smart Delivery Optimizer

API FastAPI pour optimiser l’affectation de livraisons à des véhicules avec OR-Tools.

## Prérequis

- Python 3.11
- Poetry

## Installation

```bash
poetry install
```

## Lancer l’API

```bash
poetry run uvicorn app.main:app --reload
```

Endpoints principaux :

- `GET /` : healthcheck
- `POST /optimize` : calcule une affectation de livraisons

## Exécuter les tests

```bash
poetry run pytest -q
```

## Configuration

La variable d’environnement suivante est supportée :

- `DATABASE_URL`

Comportement par défaut :

- si `DATABASE_URL` n’est pas défini, l’application utilise SQLite local (`sqlite:///./delivery_optimizer.db`)
- pour PostgreSQL, définir par exemple :

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/delivery_optimizer"
```

## Structure du projet

```text
app/
    main.py                 # Entrée FastAPI
    core/database.py        # Configuration SQLAlchemy
    models/                 # Schémas Pydantic + modèle SQLAlchemy
    services/optimizer.py   # Logique d’optimisation OR-Tools
tests/
    test_optimize.py        # Tests API
```
