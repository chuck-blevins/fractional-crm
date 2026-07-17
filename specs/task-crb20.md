# CRB-20 — FastAPI app scaffold + health + test harness

**Phase A. Depends on: none.**

Stand up the FastAPI web layer over the existing domain. Web code lives in
`src/fractional_crm/web/`; the domain package is untouched.

## Deliverables
- `requirements.txt`: `fastapi`, `uvicorn[standard]`, `jinja2`, `python-multipart`;
  `requirements-dev.txt`: `pytest`, `httpx`.
- `src/fractional_crm/web/__init__.py`.
- `src/fractional_crm/web/app.py` with `create_app() -> FastAPI` (app factory) and a module-level
  `app = create_app()` for uvicorn.
- `GET /health` → `200 {"status": "ok"}`.
- `run` script/instructions: `uvicorn fractional_crm.web.app:app --reload` (document in worklog).
- `pyproject.toml` already sets `pythonpath = ["src"]` — keep pytest working from repo root.

## Tests (scaffolded failing first)
- `tests/web/test_health.py`: `from fastapi.testclient import TestClient` + `create_app()`;
  assert `GET /health` returns `200` and JSON `{"status": "ok"}`.

## Definition of Done
- `python -m pytest -q` green (full suite, including existing domain tests).
- Domain package unchanged; no FastAPI imports leak into `src/fractional_crm/*.py`.
- Docstrings + `docs/worklog/CRB-20.md` per conventions.
