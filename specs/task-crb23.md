# CRB-23 — Engagements JSON API

**Phase B. Depends on: CRB-21 (and the error helper from CRB-22).**

Expose the existing `Engagement` domain + `SqliteEngagementRepository` over JSON.

## Deliverables (in `src/fractional_crm/web/routers/engagements.py`)
- Pydantic `EngagementIn` (client_email, role, monthly_rate, start_date, status, optional end_date)
  and `EngagementOut`. Dates are ISO `YYYY-MM-DD` strings, passed through to the domain verbatim.
- `GET /api/engagements` (optional `?client_email=` filter) → `200`.
- `POST /api/engagements` → `201`; `422` when the domain raises (monthly_rate<=0, end_date<start_date,
  bad role/status/email); `409` on duplicate for that client key.
- `GET/PUT/DELETE /api/engagements/{id}` → `200`/`404` (and `422` on invalid PUT).
- Reuse `web/errors.py` mapping. Do not re-validate in the web layer.

## Tests
- `tests/web/test_engagements_api.py`: happy paths, `422` on `monthly_rate<=0` and on
  `end_date<start_date`, list filter by `client_email`, `404` on missing.

## Definition of Done
- `python -m pytest -q` green. Docstrings + `docs/worklog/CRB-23.md` per conventions.
