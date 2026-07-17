"""CRB-39: in-process login rate limiting and lockout."""
import time
from typing import Callable, Dict, Tuple
import threading
import math
import os

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
        self._store: Dict[str, Tuple[int, float | None]] = {}
        self._lock = threading.Lock()

    def is_locked(self, key: str) -> bool:
        """Return True while ``key`` is inside its lockout window."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return False
            count, locked_until = entry
            if locked_until is None:
                return False
            if self._clock() < locked_until:
                return True
            del self._store[key]
            return False

    def retry_after(self, key: str) -> int:
        """Whole seconds until ``key`` unlocks, rounded up; 0 if not locked."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return 0
            count, locked_until = entry
            if locked_until is None or self._clock() >= locked_until:
                return 0
            return math.ceil(locked_until - self._clock())

    def record_failure(self, key: str) -> None:
        """Count a failed login for ``key``, locking it out at the threshold."""
        with self._lock:
            count = self._store[key][0] + 1 if key in self._store else 1
            if count >= self._max_failures:
                locked_until = self._clock() + self._lockout_seconds
            else:
                locked_until = None
            self._store[key] = (count, locked_until)

    def record_success(self, key: str) -> None:
        """Forget ``key`` entirely after a successful login."""
        with self._lock:
            if key in self._store:
                del self._store[key]


def limiter_from_env() -> LoginRateLimiter:
    """Build a limiter from CRM_LOGIN_MAX_FAILURES / CRM_LOGIN_LOCKOUT_SECONDS.

    Missing, empty or unparseable values fall back to the DEFAULT_* constants: a typo in an
    env var must never stop the app from starting.
    """
    try:
        max_failures = int(os.environ["CRM_LOGIN_MAX_FAILURES"])
    except (KeyError, ValueError, TypeError):
        max_failures = DEFAULT_MAX_FAILURES
    try:
        lockout_seconds = float(os.environ["CRM_LOGIN_LOCKOUT_SECONDS"])
    except (KeyError, ValueError, TypeError):
        lockout_seconds = DEFAULT_LOCKOUT_SECONDS
    return LoginRateLimiter(max_failures=max_failures, lockout_seconds=lockout_seconds)
