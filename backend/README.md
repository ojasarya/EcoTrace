# EcoTrace API

The EcoTrace API is a modular FastAPI backend for the industrial emissions
platform. It currently exposes the application entry point, a health endpoint,
configuration, a PostgreSQL connection foundation, and the first versioned
database schema for factory activity and emissions data.

## Requirements

- Python 3.11+
- `pip`
- PostgreSQL 14+ for database connectivity

## Setup

From the `backend` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Local PostgreSQL setup

Install PostgreSQL using the installer for your operating system, then create
the local database:

```sql
CREATE DATABASE ecotrace;
```

Copy `.env.example` to `.env` and set `DATABASE_URL` to the PostgreSQL
connection string for your local installation. Do not commit `.env` or put
real credentials in `.env.example`.

Apply the initial schema from the `backend` directory with:

```powershell
python -m alembic upgrade head
```

The API does not create database tables automatically. Use Alembic for all
schema changes.

## Seed demo data

After applying migrations, from the `backend` directory run:

```powershell
python -m scripts.seed_demo
```

The command creates one factory, a reporting period, representative activity
data, emission factors, interventions, and a persisted calculation. It is
idempotent for the `EcoTrace Demo Factory` record.

## Run the API

From the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

The interactive API documentation is available at
`http://127.0.0.1:8000/docs`.

## Health check

```text
GET http://127.0.0.1:8000/api/v1/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "ecotrace-api"
}
```

## Tests

From the `backend` directory:

```powershell
python -m pytest
```

The test suite does not require a live PostgreSQL server. Database connectivity
can be checked separately with `app.db.session.check_database_connection`.
