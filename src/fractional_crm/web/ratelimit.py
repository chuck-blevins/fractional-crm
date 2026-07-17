"""CRB-39: in-process login rate limiting and lockout.

STUB — not yet implemented. The behaviour is specified by specs/task-crb39.md and pinned by
tests/web/test_login_ratelimit.py. Every method below is a deliberate no-op so the app still
builds and the pre-existing suite still passes: the CRB-39 tests are the only thing red.
"""
import time
from typing import Callable

DEFAULT_MAX_FAILURES = 5
DEFAULT_LOCKOUT_SECONDS = 300.0


class LoginRateLimiter:
    """Track consecutive failed logins per client key and lock the key out past a threshold."""

    def __init__(
        self,
        max_failures: int = DEFAULT_MAX_FAILURES,
        lockout_seconds: float = DEFAULT_LOCKOUT_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Store the thresholds and the (injectable) monotonic clock."""
        self._max_failures = max_failures
        self._lockout_seconds = lockout_seconds
        self._clock = clock

    def is_locked(self, key: str) -> bool:
        """Return True while ``key`` is inside its lockout window. STUB: always False."""
        return False

    def retry_after(self, key: str) -> int:
        """Whole seconds until ``key`` unlocks, rounded up; 0 if not locked. STUB: always 0."""
        return 0

    def record_failure(self, key: str) -> None:
        """Count a failed login for ``key``, locking it out at the threshold. STUB: no-op."""

    def record_success(self, key: str) -> None:
        """Forget ``key`` entirely after a successful login. STUB: no-op."""


def limiter_from_env() -> LoginRateLimiter:
    """Build a limiter from CRM_LOGIN_MAX_FAILURES / CRM_LOGIN_LOCKOUT_SECONDS. STUB: defaults."""
    return LoginRateLimiter()
