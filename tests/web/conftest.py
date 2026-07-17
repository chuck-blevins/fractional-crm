"""Shared web-test fixtures: an authenticated TestClient on an isolated temp DB.

CRB-28 gates every /api route behind a signed session. So the shared ``client``
fixture now logs in (single-user passcode auth) before yielding, keeping the rest
of the web suite exercising the real, authenticated app. Auth is covered directly
in ``test_auth.py`` with its own un-authenticated client.
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
def client(tmp_path, monkeypatch) -> TestClient:
    """Yield an authenticated TestClient bound to a fresh, empty temp database."""
    monkeypatch.setenv("CRM_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CRM_SESSION_SECRET", "test-secret-not-for-prod")
    monkeypatch.setenv("CRM_PASSCODE_HASH", _passcode_hash(_TEST_PASSCODE))
    c = TestClient(create_app())
    # Establish the session cookie; before CRB-28 lands this is a no-op (login 404s)
    # and the auth-dependent tests correctly show red.
    c.post("/login", data={"passcode": _TEST_PASSCODE})
    return c
