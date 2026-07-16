"""Shared web-test fixtures: a TestClient bound to an isolated temp SQLite DB per test."""
import pytest
from fastapi.testclient import TestClient

from fractional_crm.web.app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    """Yield a TestClient whose CRM_DB_PATH points at a fresh, empty temp database."""
    monkeypatch.setenv("CRM_DB_PATH", str(tmp_path / "test.db"))
    return TestClient(create_app())
