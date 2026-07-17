"""Shared web-test fixtures: authenticated + anonymous TestClients on an isolated temp DB.

CRB-28 gates every /api route (and the UI pages) behind a signed session. The ``client``
fixture logs in so the rest of the web suite exercises the real authenticated app;
``anon_client`` stays logged out for gating/redirect assertions.
"""
import hashlib
import secrets

import pytest
from fastapi.testclient import TestClient

from fractional_crm.web.app import create_app

_PBKDF2_ITERATIONS = 200_000
_TEST_PASSCODE = "246810"


def _passcode_hash(passcode: str) -> str:
    """Build a CRM_PASSCODE_HASH value (``<salt_hex>$<pbkdf2_sha256_hex>``)."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", passcode.encode(), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


@pytest.fixture
def _web_env(tmp_path, monkeypatch):
    """Configure an isolated DB, session secret, and app passcode hash for a test."""
    monkeypatch.setenv("CRM_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CRM_SESSION_SECRET", "test-secret-not-for-prod")
    monkeypatch.setenv("CRM_PASSCODE_HASH", _passcode_hash(_TEST_PASSCODE))


@pytest.fixture
def anon_client(_web_env) -> TestClient:
    """Yield an un-authenticated TestClient on a fresh, empty temp database."""
    return TestClient(create_app())


@pytest.fixture
def client(_web_env) -> TestClient:
    """Yield an authenticated TestClient bound to a fresh, empty temp database."""
    c = TestClient(create_app())
    # Establish the session cookie; before CRB-28 landed this was a no-op (login 404s).
    c.post("/login", data={"passcode": _TEST_PASSCODE})
    return c
