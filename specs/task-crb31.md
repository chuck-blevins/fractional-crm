# CRB-31 — Engagements UI + reporting dashboard

**Phase D. Depends on: CRB-23, CRB-26, CRB-29.**

## Deliverables
- `GET /engagements` — list (filterable by client), create/edit forms enforcing `monthly_rate > 0`
  and `end_date >= start_date` (surface the domain error accessibly). Enum `<select>`s for role/status.
- Dashboard widgets on `/` (fill the CRB-29 slots): **Active engagements** count and **Monthly
  run-rate** from `GET /api/reporting/summary`. Currency-formatted; run-rate shows `$0` when none.

## Tests
- `tests/web/test_engagements_ui.py`: create form rejects `monthly_rate<=0` and `end_date<start_date`
  with an accessible error; the dashboard renders the run-rate value from the reporting summary.

## Definition of Done
- `python -m pytest -q` green. Docstrings/comments + `docs/worklog/CRB-31.md` per conventions.
