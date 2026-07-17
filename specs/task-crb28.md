# CRB-28 — Session login (passcode auth) + route protection

**Phase C. Depends on: CRB-20. Reviewer may tighten — auth is security-sensitive.**

Single-user app login using the existing `passcode` domain (PBKDF2, constant-time compare). Gate
the app behind a signed session cookie.

## Deliverables (in `src/fractional_crm/web/auth.py`)
- Starlette `SessionMiddleware` with a secret from env `CRM_SESSION_SECRET` (required; app refuses
  to start without it in production). Document in `.env.example`.
- The app passcode hash comes from env `CRM_PASSCODE_HASH` (never store the plaintext). Provide a
  tiny helper/CLI note to generate it via the existing passcode module.
- `GET /login` (form) and `POST /login` — verify via the existing passcode verifier; on success set
  the session and redirect to `/`; on failure re-render with an error (no user enumeration).
- `POST /logout` clears the session.
- Dependency `require_session` protecting all routes EXCEPT `/health`, `/login`, `/logout`, and
  static assets. Unauthenticated JSON request → `401`; unauthenticated page request → redirect to `/login`.

## Tests
- `tests/web/test_auth.py`: protected route without session → `401`/redirect; wrong passcode → stays
  logged out; correct passcode → session set and protected route returns `200`; `/health` stays public.

## Definition of Done
- `python -m pytest -q` green. No secrets committed. Docstrings + `docs/worklog/CRB-28.md` per conventions.
