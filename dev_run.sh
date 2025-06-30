#!/bin/bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit autoupdate
uv run pre-commit run --all-files

# Run the application locally
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
