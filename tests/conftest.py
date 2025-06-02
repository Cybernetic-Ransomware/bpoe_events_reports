import pytest


@pytest.fixture(scope="function")
def app(monkeypatch):
    monkeypatch.setenv("DEBUG", "True")

    from src.main import app as fastapi_app
    return fastapi_app
