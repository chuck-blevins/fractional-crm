"""CRB-39 acceptance tests: rate limiting + lockout on /login.

Security review 2026-07-17, finding 1. Two layers are specified here:

* the pure :class:`LoginRateLimiter` unit (deterministic, driven by an injected fake clock), and
* the wired ``POST /login`` endpoint, including the property that a locked-out request is
  rejected *before* PBKDF2 runs — the lockout is a CPU-exhaustion defence as much as a
  brute-force defence, so hashing first would defeat its purpose.
"""
import hashlib
import secrets

import pytest
from fastapi.testclient import TestClient

from fractional_crm.web import auth
from fractional_crm.web.app import create_app
from fractional_crm.web.ratelimit import (
    DEFAULT_LOCKOUT_SECONDS,
    DEFAULT_MAX_FAILURES,
    LoginRateLimiter,
    limiter_from_env,
)

_PBKDF2_ITERATIONS = 200_000
PASSCODE = "246810"


class FakeClock:
    """A manually advanced monotonic clock, so lockout expiry is testable without sleeping."""

    def __init__(self) -> None:
        self.now = 1_000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _make_hash(passcode: str) -> str:
    """Produce a CRM_PASSCODE_HASH string using the documented PBKDF2 scheme."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", passcode.encode(), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


# --------------------------------------------------------------------------- unit


def test_under_the_limit_is_not_locked() -> None:
    lim = LoginRateLimiter(max_failures=3, lockout_seconds=60, clock=FakeClock())
    lim.record_failure("ip")
    lim.record_failure("ip")
    assert lim.is_locked("ip") is False
    assert lim.retry_after("ip") == 0


def test_locks_when_failures_reach_max() -> None:
    lim = LoginRateLimiter(max_failures=3, lockout_seconds=60, clock=FakeClock())
    for _ in range(3):
        lim.record_failure("ip")
    assert lim.is_locked("ip") is True
    assert 0 < lim.retry_after("ip") <= 60


def test_lockout_expires_and_fully_resets() -> None:
    clock = FakeClock()
    lim = LoginRateLimiter(max_failures=3, lockout_seconds=60, clock=clock)
    for _ in range(3):
        lim.record_failure("ip")
    assert lim.is_locked("ip") is True

    clock.advance(61)
    assert lim.is_locked("ip") is False
    assert lim.retry_after("ip") == 0

    # A full reset: one further failure must NOT immediately re-lock.
    lim.record_failure("ip")
    assert lim.is_locked("ip") is False


def test_success_clears_failures() -> None:
    lim = LoginRateLimiter(max_failures=3, lockout_seconds=60, clock=FakeClock())
    lim.record_failure("ip")
    lim.record_failure("ip")
    lim.record_success("ip")
    lim.record_failure("ip")
    assert lim.is_locked("ip") is False


def test_keys_are_independent() -> None:
    lim = LoginRateLimiter(max_failures=2, lockout_seconds=60, clock=FakeClock())
    lim.record_failure("1.1.1.1")
    lim.record_failure("1.1.1.1")
    assert lim.is_locked("1.1.1.1") is True
    assert lim.is_locked("2.2.2.2") is False


def test_retry_after_counts_down_and_rounds_up() -> None:
    clock = FakeClock()
    lim = LoginRateLimiter(max_failures=1, lockout_seconds=60, clock=clock)
    lim.record_failure("ip")
    assert lim.retry_after("ip") == 60
    clock.advance(30.5)
    assert lim.retry_after("ip") == 30  # 29.5 remaining -> ceil -> 30


def test_limiter_from_env_defaults(monkeypatch) -> None:
    monkeypatch.delenv("CRM_LOGIN_MAX_FAILURES", raising=False)
    monkeypatch.delenv("CRM_LOGIN_LOCKOUT_SECONDS", raising=False)
    lim = limiter_from_env()
    assert lim._max_failures == DEFAULT_MAX_FAILURES
    assert lim._lockout_seconds == DEFAULT_LOCKOUT_SECONDS


def test_limiter_from_env_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("CRM_LOGIN_MAX_FAILURES", "2")
    monkeypatch.setenv("CRM_LOGIN_LOCKOUT_SECONDS", "30")
    lim = limiter_from_env()
    assert lim._max_failures == 2
    assert lim._lockout_seconds == 30


def test_limiter_from_env_survives_garbage(monkeypatch) -> None:
    """A typo'd env value must fall back to the default, never crash the app at startup."""
    monkeypatch.setenv("CRM_LOGIN_MAX_FAILURES", "five")
    monkeypatch.setenv("CRM_LOGIN_LOCKOUT_SECONDS", "")
    lim = limiter_from_env()
    assert lim._max_failures == DEFAULT_MAX_FAILURES
    assert lim._lockout_seconds == DEFAULT_LOCKOUT_SECONDS


# --------------------------------------------------------------------- integration


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Isolated DB + secret + passcode hash, with a deliberately tiny lockout threshold."""
    monkeypatch.setenv("CRM_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CRM_SESSION_SECRET", "unit-test-secret-not-for-prod")
    monkeypatch.setenv("CRM_PASSCODE_HASH", _make_hash(PASSCODE))
    monkeypatch.setenv("CRM_LOGIN_MAX_FAILURES", "3")
    monkeypatch.setenv("CRM_LOGIN_LOCKOUT_SECONDS", "300")


def _client(env_ready, host="1.2.3.4") -> TestClient:
    return TestClient(create_app(), follow_redirects=False, client=(host, 5000))


def test_lockout_after_max_failed_logins(env) -> None:
    c = _client(env)
    for _ in range(3):
        assert c.post("/login", data={"passcode": "wrong"}).status_code == 200
    r = c.post("/login", data={"passcode": "wrong"})
    assert r.status_code == 429
    assert int(r.headers["retry-after"]) > 0


def test_locked_out_rejects_even_the_CORRECT_passcode(env) -> None:
    """No oracle: while locked, a correct passcode must be refused exactly like a wrong one."""
    c = _client(env)
    for _ in range(3):
        c.post("/login", data={"passcode": "wrong"})
    r = c.post("/login", data={"passcode": PASSCODE})
    assert r.status_code == 429
    assert "session" not in r.cookies


def test_locked_out_request_never_runs_pbkdf2(env, monkeypatch) -> None:
    """The lockout is a CPU defence too: a locked request must short-circuit before hashing."""
    c = _client(env)
    for _ in range(3):
        c.post("/login", data={"passcode": "wrong"})

    calls = []
    real = auth.verify_passcode
    monkeypatch.setattr(auth, "verify_passcode", lambda *a, **k: calls.append(1) or real(*a, **k))

    assert c.post("/login", data={"passcode": "wrong"}).status_code == 429
    assert calls == [], "verify_passcode ran while locked out — PBKDF2 CPU burn is unguarded"


def test_successful_login_resets_the_counter(env) -> None:
    c = _client(env)
    c.post("/login", data={"passcode": "wrong"})
    c.post("/login", data={"passcode": "wrong"})
    assert c.post("/login", data={"passcode": PASSCODE}).status_code == 303

    c2 = _client(env)
    for _ in range(2):
        assert c2.post("/login", data={"passcode": "wrong"}).status_code == 200


def test_lockout_is_per_client(env) -> None:
    app = create_app()
    attacker = TestClient(app, follow_redirects=False, client=("6.6.6.6", 5000))
    victim = TestClient(app, follow_redirects=False, client=("7.7.7.7", 5000))
    for _ in range(3):
        attacker.post("/login", data={"passcode": "wrong"})
    assert attacker.post("/login", data={"passcode": "wrong"}).status_code == 429
    assert victim.post("/login", data={"passcode": PASSCODE}).status_code == 303
