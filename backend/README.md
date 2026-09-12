# EcoTrace API

The EcoTrace API is a modular FastAPI backend for the industrial emissions
platform. This initial foundation exposes the application entry point and a
health endpoint only. Domain, database, and calculation modules will be added
in their approved implementation steps.

## Requirements

- Python 3.11+
- `pip`

## Setup

From the `backend` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

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
