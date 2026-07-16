# CRB-25 — Teams + Integrations JSON API

**Phase B. Depends on: CRB-21.**

Expose the existing `Team`/`TeamMember` and `Integration`/`IntegrationRegistry` domain over JSON.
Persist them following the existing repository idioms (extend the SQLite layer if needed).

## Deliverables (in `src/fractional_crm/web/routers/teams.py` and `integrations.py`)
- Teams: `POST /api/teams` (name) → `201`; `GET /api/teams` → `200`;
  `POST /api/teams/{id}/members` (name, email, role in admin/member/guest) → `201`, `422` bad role,
  `409` duplicate (team,email); `GET /api/teams/{id}/members` (optional `?role=`).
- Integrations: `GET /api/integrations` → `200`; `POST /api/integrations` (provider, external_id) →
  `201`, `422` bad provider, `409` duplicate provider; `DELETE /api/integrations/{provider}` →
  `204`/`404`; `POST /api/integrations/{provider}/sync` → `200` sets `last_synced` + status connected.
- Reuse `web/errors.py`.

## Tests
- `tests/web/test_teams_api.py`, `tests/web/test_integrations_api.py`: member add + duplicate,
  role filter, connect/disconnect/sync, `404` unknown provider, enum rejection.

## Definition of Done
- `python -m pytest -q` green. Docstrings + `docs/worklog/CRB-25.md` per conventions.
