# CRB-39 — Rate limit + lockout on `/login`

Security review 2026-07-17, finding 1 (HIGH). Must close before CRB-35 (deploy).

## Why

The whole app is protected by ONE passcode and nothing limits guessing it: 12 wrong passcodes
in a row all returned HTTP 200, no throttle anywhere. The only brake is PBKDF2's ~134ms, which
parallelises away. That same 134ms is also *unauthenticated CPU* — so the lockout check MUST
run **before** the hash, or the fix makes the DoS worse.

## Your task (this run): build `src/fractional_crm/web/ratelimit.py` ONLY

The file already exists as a stub. **Edit it in place.** Do not create any other file. Do not
touch `auth.py`, `app.py`, or any test — the wiring and the tests are already written.

Pure stdlib. No new dependency. Single in-process deploy, but the handlers are sync `def` and
run in a threadpool, so the state **must be guarded by a `threading.Lock`**.

## Exact interface (the tests import exactly these names)

```python
DEFAULT_MAX_FAILURES = 5
DEFAULT_LOCKOUT_SECONDS = 300.0


class LoginRateLimiter:
    def __init__(
        self,
        max_failures: int = DEFAULT_MAX_FAILURES,
        lockout_seconds: float = DEFAULT_LOCKOUT_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None: ...

    def is_locked(self, key: str) -> bool: ...
    def retry_after(self, key: str) -> int: ...
    def record_failure(self, key: str) -> None: ...
    def record_success(self, key: str) -> None: ...


def limiter_from_env() -> LoginRateLimiter: ...
```

## Exact semantics

- `record_failure(key)` increments that key's consecutive-failure count. When the count
  **reaches** `max_failures`, the key becomes locked until `clock() + lockout_seconds`.
- `is_locked(key)` → True only while `clock() < locked_until`. When the lockout has expired,
  the key **resets completely** (count back to 0, unlocked) — one expiry does not leave it
  one-strike-from-locked.
- `retry_after(key)` → whole seconds remaining, rounded UP (`math.ceil`); `0` when not locked.
- `record_success(key)` → forget the key entirely (count 0, not locked).
- Keys are **independent**: locking `"1.1.1.1"` must not affect `"2.2.2.2"`.
- `clock` is injectable so tests can advance time without sleeping. Call `self._clock()`, never
  `time.monotonic()` directly, anywhere.
- **Prune** entries that are expired and have no active lockout when you touch the map, so a
  long-lived process cannot grow unbounded from random source IPs.
- `limiter_from_env()` reads `CRM_LOGIN_MAX_FAILURES` and `CRM_LOGIN_LOCKOUT_SECONDS`,
  falling back to the DEFAULT_* constants when unset **or unparseable** (never crash on a bad
  env value — a typo must not take the app down).

## Definition of done

- `.venv/bin/python -m pytest -q tests/web/test_login_ratelimit.py` fully green.
- Full suite still green.
- Every public name carries a real docstring (module, class, every method).
- No file created or modified other than `src/fractional_crm/web/ratelimit.py`.
