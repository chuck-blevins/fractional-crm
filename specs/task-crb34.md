# CRB-34 — CSV import/export UI

**Phase D. Depends on: CRB-27, CRB-29.**

## Deliverables
- On `/clients`: an **Export CSV** link (`GET /api/clients/export`) and an **Import** form that
  uploads a CSV/JSON file to `POST /api/clients/import` (multipart, accessible file input + label).
- After import, render a result summary: imported count + a per-row error list (row number + message)
  in an accessible region. Controls disabled while a request is in flight; malformed/oversize handled gracefully.

## Tests
- `tests/web/test_csv_ui.py`: import form renders the returned per-row errors; export link points at
  the export endpoint.

## Definition of Done
- `python -m pytest -q` green. Docstrings/comments + `docs/worklog/CRB-34.md` per conventions.
