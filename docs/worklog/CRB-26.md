# CRB-26 — Reporting API

**What was built**
`web/routers/reporting.py` — `GET /api/reporting/summary` returning `{active_count, monthly_run_rate}`,
computed by calling the existing domain `active_engagements` / `monthly_run_rate` over the engagement
repo's full list. No math duplicated in the web layer.

**How it was built (the loop)**
- Claude scaffolded `test_reporting_api.py` (2 cases, red).
- qwen2.5-coder-7b via aider (router + app wiring), zero bounces. File-location verified non-empty at
  the intended path (applying the CRB-25 lesson).

**Test coverage**
- empty repo -> `{active_count:0, monthly_run_rate:0}`; mixed statuses -> active count + run-rate match
  the domain functions. Full suite green.
