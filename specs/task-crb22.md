# CRB-22 — Clients JSON API (CRUD + status transition)

**Phase B. Depends on: CRB-21. Model sweet spot: TestClient tests over the existing domain.**

Expose the existing `Client` domain + `SqliteClientRepository` over JSON. Reuse domain validation —
do NOT re-validate in the web layer; catch and map its errors.

## Deliverables (in `src/fractional_crm/web/routers/clients.py`)
- Pydantic `ClientIn` (name, company, email, status, engagement_type) and `ClientOut`.
- `GET /api/clients` → `200` list of clients.
- `POST /api/clients` → `201` created; `422` if the domain `Client(...)` raises `ValueError`;
  `409` if the repository raises on a duplicate email.
- `GET /api/clients/{email}` → `200` / `404` (repo `KeyError`).
- `PUT /api/clients/{email}` → `200` / `422` / `404`.
- `DELETE /api/clients/{email}` → `204` / `404`.
- `POST /api/clients/{email}/status` body `{"status": "..."}` → `200` on an allowed
  `Client.transition_to`, `422` on a disallowed transition (status unchanged), `404` if missing.
- Register the router in `create_app()`. Shared error mapping helper
  (`web/errors.py`: ValueError→422, KeyError→404) — reused by later routers.

## Tests
- `tests/web/test_clients_api.py`: create/list/get/update/delete happy paths; `422` on bad email;
  `409` on duplicate; `404` on missing; allowed vs disallowed status transition.

## Definition of Done
- `python -m pytest -q` green. Docstrings + `docs/worklog/CRB-22.md` per conventions.
