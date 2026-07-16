# CRB-21 — Config + SQLite wiring

**Phase A. Depends on: CRB-20.**

Wire the web app to the existing SQLite repositories via a swappable dependency, so tests use a
temp DB and production uses a configured path.

## Deliverables
- `src/fractional_crm/web/config.py`: read `CRM_DB_PATH` from env (default `crm.db`).
- `src/fractional_crm/web/deps.py`: FastAPI dependencies `get_client_repo()` and
  `get_engagement_repo()` returning `SqliteClientRepository` / `SqliteEngagementRepository`
  (from the existing `sqlite_repository` module) opened on the configured path. Ensure the
  SQLite schema/tables exist (reuse whatever the repo already does on init).
- Wire the app so `create_app()` respects `CRM_DB_PATH` and overrides are possible in tests
  (FastAPI `app.dependency_overrides`).
- A pytest fixture `client(tmp_path)` in `tests/web/conftest.py` that points `CRM_DB_PATH` at a
  temp file (or overrides the deps) and yields a `TestClient` with an isolated empty DB per test.

## Tests
- `tests/web/test_wiring.py`: two requests in one test session persist data across calls within a
  test but NOT across tests (isolation holds); a fresh `client` fixture starts empty.

## Definition of Done
- `python -m pytest -q` green. Docstrings + `docs/worklog/CRB-21.md` per conventions.
