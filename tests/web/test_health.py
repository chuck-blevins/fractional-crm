"""CRB-20 acceptance test: the FastAPI app exposes a public health probe."""
from fastapi.testclient import TestClient

from fractional_crm.web.app import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
