# CRB-27 — CSV import/export API

**Phase B. Depends on: CRB-22.**

Expose the existing `csv_io` / `importer` domain over HTTP. Reuse the existing export/import +
formula-injection handling — do not re-implement.

## Deliverables (in `src/fractional_crm/web/routers/csv_routes.py`)
- `GET /api/clients/export` → `200`, `Content-Type: text/csv`,
  `Content-Disposition: attachment; filename="clients.csv"`; body from the existing
  `export_clients_csv` (formula-injection escaping already applied in the domain).
- `POST /api/clients/import` — accept a multipart file **or** raw CSV/JSON body; run the existing
  `ClientImporter` against the repository; return `200 {"imported": int, "errors": [...]}` with the
  per-row errors from the importer. Malformed payload → `400`. Cap size (> 5 MB → `413`).

## Tests
- `tests/web/test_csv_api.py`: export header + body; import a mixed valid/invalid payload returns
  per-row errors; export→import round-trip; oversize `413`.

## Definition of Done
- `python -m pytest -q` green. Docstrings + `docs/worklog/CRB-27.md` per conventions.
