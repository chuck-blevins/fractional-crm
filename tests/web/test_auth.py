"""CRB-28 acceptance tests: single-user passcode login + route protection.

These tests are the spec for ``src/fractional_crm/web/auth.py``. They pin:
  * the ``CRM_PASSCODE_HASH`` format = ``<salt_hex>$<pbkdf2_sha256_hex>`` (200k iters),
  * a signed-session login flow gated by ``CRM_SESSION_SECRET``,
  * ``require_session`` gating: unauth JSON (``/api/...``) -> 401, unauth page -> redirect to /login,
  * ``/health``, ``/login``, ``/logout`` staying public.
Do not weaken or delete anything here.
"""
import hashlib
import secrets

import pytest
from fastapi.testclient import TestClient

from fractional_crm.web.app import create_app

_PBKDF2_ITERATIONS = 200_000
PASSCODE = "246810"


def _make_hash(passcode: str, salt: bytes | None = None) -> str:
    """Produce a CRM_PASSCODE_HASH string using the documented PBKDF2 scheme."""
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", passcode.encode(), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Configure an isolated DB, a session secret, and the app passcode hash."""
    monkeypatch.setenv("CRM_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CRM_SESSION_SECRET", "unit-test-secret-not-for-prod")
    monkeypatch.setenv("CRM_PASSCODE_HASH", _make_hash(PASSCODE))


@pytest.fixture
def anon(env) -> TestClient:
    """An un-authenticated TestClient (no login performed)."""
    return TestClient(create_app())


def _login(c: TestClient, passcode: str):
    return c.post("/login", data={"passcode": passcode}, follow_redirects=False)


# --- public endpoints -------------------------------------------------------

def test_health_is_public(anon):
    assert anon.get("/health").status_code == 200
    assert anon.get("/health").json() == {"status": "ok"}


def test_login_page_is_public_and_accessible(anon):
    r = anon.get("/login")
    assert r.status_code == 200
    body = r.text.lower()
    # Accessible form: a real <form>, a labelled passcode field, a submit control.
    assert "<form" in body
    assert "<label" in body
    assert 'name="passcode"' in body


# --- gating without a session ----------------------------------------------

def test_protected_api_without_session_is_401(anon):
    assert anon.get("/api/clients").status_code == 401


def test_protected_page_without_session_redirects_to_login(anon):
    r = anon.get("/", follow_redirects=False)
    assert r.status_code in (302, 303, 307)
    assert "/login" in r.headers["location"]


# --- login / logout flow ----------------------------------------------------

def test_wrong_passcode_stays_logged_out(anon):
    r = _login(anon, "000000")
    # Re-renders the login page with an error, does NOT set an authenticated session.
    assert r.status_code == 200
    assert "error" in r.text.lower() or "incorrect" in r.text.lower()
    # Still gated afterwards.
    assert anon.get("/api/clients").status_code == 401


def test_correct_passcode_logs_in_and_unlocks(anon):
    r = _login(anon, PASSCODE)
    assert r.status_code in (302, 303, 307)
    assert r.headers["location"] in ("/", "http://testserver/")
    # Session cookie now on the client -> protected routes open up.
    assert anon.get("/api/clients").status_code == 200
    assert anon.get("/", follow_redirects=False).status_code == 200


def test_logout_clears_session(anon):
    assert _login(anon, PASSCODE).status_code in (302, 303, 307)
    assert anon.get("/api/clients").status_code == 200
    out = anon.post("/logout", follow_redirects=False)
    assert out.status_code in (302, 303, 307)
    assert "/login" in out.headers["location"]
    # Re-gated after logout.
    assert anon.get("/api/clients").status_code == 401


# --- passcode hash helper contract -----------------------------------------

def test_hash_helper_roundtrip_and_format():
    from fractional_crm.web.auth import hash_passcode, verify_passcode

    stored = hash_passcode(PASSCODE)
    salt_hex, _, digest_hex = stored.partition("$")
    assert salt_hex and digest_hex  # "<salt_hex>$<digest_hex>"
    bytes.fromhex(salt_hex)         # both halves are hex
    bytes.fromhex(digest_hex)
    assert verify_passcode(PASSCODE, stored) is True
    assert verify_passcode("999999", stored) is False
    # Interoperable with an independently-computed hash of the same scheme.
    assert verify_passcode(PASSCODE, _make_hash(PASSCODE)) is True
