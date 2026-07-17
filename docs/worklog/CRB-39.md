# CRB-39 — Rate limit + lockout on `/login`

Closes finding 1 of the 2026-07-17 security review (docs/SECURITY_REVIEW.md). Was the last
HIGH blocking CRB-35 (deploy).

## Problem
The whole app is protected by one passcode and nothing limited guessing it: 12 consecutive wrong
passcodes all returned HTTP 200, and no throttle existed anywhere in `src/`. The only brake was
PBKDF2's ~134 ms/attempt (~7/sec per connection), which parallelises away.

## What was built
- **`web/ratelimit.py`** (new): `LoginRateLimiter` — per-key consecutive-failure counter with a
  lockout window, guarded by a `threading.Lock` (handlers are sync `def` and run in a threadpool).
  - `record_failure` locks a key only once its count **reaches** `max_failures`.
  - `is_locked` returns True only inside the window; an **expired lockout fully resets** the key
    (one further failure must not immediately re-lock).
  - `retry_after` → `math.ceil` of the remaining seconds, 0 when unlocked.
  - `record_success` forgets the key.
  - Injected `clock` (defaults to `time.monotonic`) so expiry is testable without sleeping.
  - `limiter_from_env()` reads `CRM_LOGIN_MAX_FAILURES` / `CRM_LOGIN_LOCKOUT_SECONDS` and falls
    back to defaults on missing/empty/**unparseable** values — a typo must never stop startup.
- **`web/auth.py`**: `client_key()` + the lockout check in the `/login` handler.
- **`web/app.py`**: per-app limiter on `app.state.login_limiter`, so every app instance (and every
  test) gets clean state.

## Key decisions
- **The lockout check runs BEFORE `verify_passcode`.** PBKDF2 costs ~134 ms of CPU per call, so
  hashing a locked-out attempt would leave `/login` usable as a cheap CPU-exhaustion vector — the
  very thing the lockout exists to stop. Pinned by `test_locked_out_request_never_runs_pbkdf2`,
  which spies on `verify_passcode` and asserts it is never called while locked.
- **No oracle.** A locked client gets an identical 429 whether the passcode is right or wrong.
- **`client_key` uses the peer IP, deliberately NOT `X-Forwarded-For`.** XFF is attacker-supplied
  unless a trusted proxy overwrites it; honouring it blindly would let anyone bypass the lockout by
  varying a header. If CRB-35 puts this behind a proxy, configure uvicorn `--proxy-headers` with an
  explicit `--forwarded-allow-ips` rather than reading XFF here.
- **PBKDF2 stays at 200k** (not raised to OWASP's 600k): tripling it also triples the
  unauthenticated CPU cost. Rate limiting first; revisit iterations separately.

## Test coverage (`tests/web/test_login_ratelimit.py`, 14 tests)
Unit (fake clock): under-limit not locked; locks at threshold; expiry fully resets; success clears;
keys independent; `retry_after` counts down and rounds up; env defaults, env parsing, and garbage
env falls back. Integration: 429 + `Retry-After` after max failures; correct passcode also refused
while locked; locked request never runs PBKDF2; success resets the counter; lockout is per-client.
**Full suite: 281 passed.**

## Build notes (local-LLM loop)
`ratelimit.py` built by qwen2.5-coder-7b via aider — **2 runs (1 bounce)**.

- **Run 1** produced a plausible-but-wrong limiter with two spec violations: it set `locked_until`
  on *every* failure (so one wrong passcode locked you out — it never compared count to
  `max_failures`), and `limiter_from_env` used a bare `int(os.getenv(...))` that raised
  `ValueError` on a typo. Both were explicit spec bullets. Consistent with the known ceiling: the
  7B is a good drafter, not a finisher — conditional/edge rules need the exact code spoon-fed.
- **Run 2** (bounce with the exact code inlined) got the logic right — but hit the **path-prefix
  trap**, writing the corrected file to the repo root as `./ratelimit.py` and leaving the real
  target untouched. The content was correct; only the path was wrong, so the reviewer moved it into
  place (a path fix, not a reviewer-authored implementation).
- Note the trap fired on the **bounce**, even though the target was pre-stubbed — the pre-stub
  protects the first run (edit-not-create) but is no guarantee on later runs. See lessons.md: the
  reliable tell is aider's own `Applied edit to <path>` line.
