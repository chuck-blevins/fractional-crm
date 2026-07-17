# CRB-37 — README/USAGE update for the web app

**Phase E. Depends on: most prior stories.**

Document the app as a web app (keep the CLI docs — the CLI still works over the same domain).

## Deliverables
- Update `README.md`: what it is, quick start for the web app
  (`pip install -r requirements.txt`, set `CRM_DB_PATH`/`CRM_SESSION_SECRET`/`CRM_PASSCODE_HASH`,
  `uvicorn fractional_crm.web.app:app`), and a pointer to the Nexlayer deploy (CRB-35).
- Update `docs/USAGE.md`: add a "Web app" section (login, the six feature areas, CSV import/export)
  alongside the existing CLI/API reference. Note accessibility (WCAG 2.1 AA target).
- Keep `docs/SECURITY_REVIEW.md`; add a short note on the web layer's auth + error handling.

## Definition of Done
- Docs accurate against the shipped endpoints/pages. `python -m pytest -q` still green.
  `docs/worklog/CRB-37.md` per conventions.
