# Reports service for BPOE app
This service generates various types of event reports based on user-defined filters.
It operates as a standalone microservice in the BPOE system architecture.

## Overview
The purpose of this project is to build a reports and summaries handling microservice.

## Features
- Exposes REST API for on-demand report generation,
- Generates reports based on custom filters and parameters,
- Communicates with the `db_handler` microservice via REST,
- Validates input using Pydantic models,
- Restricts access to API gateway only,
- Supports multiple extensible report types.

## Requirements
- Python >=3.13.3 with UV package manager
- Docker Desktop / Docker + Compose

## Getting Started (Windows)
### Deploy
1. Clone the repository:
      ```powershell
      git clone https://github.com/Cybernetic-Ransomware/bpoe_events_reports.git
      ```
2. Set .env file based on the template.
3. Run using Docker:
      ```powershell
      docker-compose -f .\docker\docker-compose.yml up --build -d
      ```
### Dev-instance
1. Clone the repository:
      ```powershell
      git clone https://github.com/Cybernetic-Ransomware/bpoe_events_reports.git
      ```
2. Set .env file based on the template.
3. Install UV:
      ```powershell
      pip install uv
      ```
4. Install dependencies:
      ```powershell
      uv sync
      ```
5. Install pre-commit hooks:
      ```powershell
      uv run pre-commit install
      uv run pre-commit autoupdate
      uv run pre-commit run --all-files
      ```
6. Run the application locally:
      ```powershell
      uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
      ```

Alternatively, after step `3`, you can use the `.bat` or `.sh` init script provided.


## Testing
#### Postman
This repository includes a Postman collection ready for import into a Postman Mock Server.
[collection](docs/queries/db_handler.postman_collection.json)

#### Pytest
```powershell
uv sync --extra dev
uv run pytest
```

#### Ruff
```powershell
uv sync --extra dev
uv run ruff check
```
or as a standalone tool:
```powershell
uvx ruff check
```

#### Mypy
```powershell
uv sync --extra dev
uv run mypy .\src\
```
or as a standalone tool:
```powershell
uvx mypy .\src\
```

#### Codespell
```powershell
uv sync --extra dev
uv run codespell
```

## Useful links and documentation
- API Gateway microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe-api-gateway.git)
- Databases handler microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe_events_db_handler)
- OCR microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe-ocr)
- Reports microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe_events_reports)
