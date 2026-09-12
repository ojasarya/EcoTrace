# EcoTrace API

The EcoTrace API is a modular FastAPI backend for the industrial emissions
platform. It currently exposes the application entry point, a health endpoint,
configuration, and a PostgreSQL connection foundation. Database models and
migrations are intentionally deferred to a later implementation step.

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

The API does not create database tables automatically. Schema models and
migrations will be introduced in a later step.

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
