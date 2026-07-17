# Coding conventions (read on every task)

The app is a **Python web CRM**: a FastAPI + Jinja2/HTMX layer over the existing,
already-tested domain in `src/fractional_crm/`. We are NOT rewriting the domain — we are
exposing it over HTTP and an accessible server-rendered UI, then deploying it to Nexlayer.

## Stack
- **Python 3.12.** Domain layer (`src/fractional_crm/`): standard library only (unchanged).
- Web layer (`src/fractional_crm/web/`): **FastAPI** + **Uvicorn**, **Jinja2** templates,
  **HTMX** for partial updates, **SQLite** via the existing `sqlite_repository` module.
- Tests: **pytest** + FastAPI/Starlette **TestClient** (httpx). Tests are the spec.

## Rules
- Type hints on all public functions/classes; one-line docstrings minimum.
- Simplest correct implementation that passes the tests. Small, pure, well-named functions.
- NEVER edit, weaken, or delete anything under `tests/`. Tests are the spec.
- Import ONLY what you use — no unused imports (repeat offense in this repo; the reviewer checks).
- **Reuse the domain.** Web handlers call the existing domain models/validators/repositories.
  Do not re-implement validation in the web layer — catch the domain's `ValueError`/`KeyError`
  and map them to HTTP status codes (see below).
- Keep the domain framework-free: no FastAPI/Pydantic imports inside `src/fractional_crm/*.py`
  (only inside `src/fractional_crm/web/`).

## HTTP error mapping (consistent across all endpoints)
- Domain `ValueError` (invalid input / bad transition) → **422** (or **400** for malformed request)
- Domain `KeyError` (missing entity) → **404**
- Duplicate-key create → **409**
- Never leak stack traces; body is `{"error": "<message>"}` for JSON routes.

## Accessibility (UI stories — target WCAG 2.1 AA)
- Semantic HTML5 landmarks (`<header><nav><main>`), a skip-to-content link, one `<h1>` per page.
- Every input has an associated `<label>`; buttons have discernible text; forms work WITHOUT JS
  (HTMX is progressive enhancement, not a requirement for the action to succeed).
- Visible focus states; sufficient colour contrast; keyboard operable.

## Per-task deliverables (EVERY story — enforced in review)
1. Make the story's tests pass; the FULL suite (`python -m pytest -q`) stays green.
2. **Comprehensive annotation:** docstrings on every public function/class/route stating purpose,
   args, return, and raised/mapped errors; inline comments on non-obvious logic (auth, error
   mapping, HTMX partial vs full render, security).
3. **Work summary:** create `docs/worklog/CRB-<n>.md` — what was built, why, key decisions,
   files touched, and how the tests cover it. One screen max.

## When the local model can't finish a story
Do NOT silently have the reviewer ghostwrite it. Bounce it back with a TIGHTER spec (exact
signatures, exact error cases, exact template structure) and append a rule to
`.agent/lessons.md` so the loop improves over time. Reviewer finishes only as a last resort,
and records why in lessons.md.
