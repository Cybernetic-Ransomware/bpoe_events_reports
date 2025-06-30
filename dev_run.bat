@echo off
REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
uv sync

REM Install pre-commit hooks
uv run pre-commit install
uv run pre-commit autoupdate
uv run pre-commit run --all-files

REM Run the application locally
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
