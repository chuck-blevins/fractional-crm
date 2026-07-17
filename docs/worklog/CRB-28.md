# CRB-28 — Session login (passcode auth) + route protection

## What was built
A single-user login for the web CRM, gating every JSON API route behind a signed
session cookie.

- `src/fractional_crm/web/auth.py` (new)
  - `hash_passcode` / `verify_passcode`: PBKDF2-HMAC-SHA256 (200k iters), value format
    `<salt_hex>$<digest_hex>`, constant-time compare (`hmac.compare_digest`). Plaintext
    is never stored.
  - `session_secret()`: reads `CRM_SESSION_SECRET`; required when `CRM_ENV=production`,
    ephemeral fallback otherwise so dev/test need no config.
  - `require_session`: dependency — unauthenticated `/api/*` → **401**, unauthenticated
    page → **303 redirect to /login**.
  - Router: `GET /login` (accessible form), `POST /login` (verify → set session →
    303 to `/`, or re-render with a generic error, no user enumeration), `POST /logout`
    (clear session → 303 to `/login`), gated `GET /` placeholder home.
- `src/fractional_crm/web/app.py`: adds `SessionMiddleware(secret_key=session_secret())`,
  includes the public auth router, and applies `Depends(require_session)` to all seven
  API routers. `/health`, `/login`, `/logout` stay public.
- `tests/web/conftest.py`: the shared `client` fixture now logs in, so the existing API
  tests exercise the real authenticated app.
- `.env.example`, `requirements.txt` (+`itsdangerous`, the SessionMiddleware backend).

## Key decisions
- **Env hash, not the per-Client `PasscodeAuth`.** The domain's `PasscodeAuth` is keyed
  per Client; this is single-user app login, so the passcode hash lives in
  `CRM_PASSCODE_HASH` and is verified with the same PBKDF2 scheme/iteration count.
- **Gate via per-router `dependencies=`** rather than middleware, so exemptions
  (`/health`, `/login`, `/logout`) are simply the routers/routes without the dependency.
- **Redirect from a dependency** by raising `HTTPException(303, Location=/login)` — the
  default handler preserves the `Location` header.

## Test coverage (`tests/web/test_auth.py`)
`/health` + `/login` public; `/api/*` → 401 and pages → /login when unauthenticated;
wrong passcode stays logged out (generic error, 200); correct passcode sets the session
and unlocks `/api/*` and `/`; logout re-gates; hash helper round-trips and pins the
`<salt_hex>$<digest_hex>` format. Full suite: **260 passed**.

## Build notes (local-LLM loop)
- `auth.py` built by qwen2.5-coder-7b via aider (one-file run). One bounce fixed a
  `_login_html` string-vs-function slip and added `session_secret()`.
- `app.py` wiring: the 7B produced correct content but emitted the fence header as bare
  `app.py`, so aider wrote it to the repo root (the CRB-25 path-prefix trap). Reviewer
  moved it to the intended path. Lesson appended.
- Reviewer added the missing per-function docstrings + return hints (the recurring 7B
  docstring omission).
