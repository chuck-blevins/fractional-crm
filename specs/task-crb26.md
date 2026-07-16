# CRB-26 — Reporting API

**Phase B. Depends on: CRB-21.**

Expose the existing `reporting` domain (`active_engagements`, `monthly_run_rate`) over JSON.

## Deliverables (in `src/fractional_crm/web/routers/reporting.py`)
- `GET /api/reporting/summary` → `200 {"active_count": int, "monthly_run_rate": number}`.
  Compute over all engagements in the repository using the existing reporting functions
  (`active_engagements`, `monthly_run_rate`). `monthly_run_rate` is `0` when none active.
- Do not duplicate the reporting math — call the domain functions.

## Tests
- `tests/web/test_reporting_api.py`: empty repo → `{active_count:0, monthly_run_rate:0}`;
  with mixed-status engagements the counts/total match the domain functions.

## Definition of Done
- `python -m pytest -q` green. Docstrings + `docs/worklog/CRB-26.md` per conventions.
