# CRB-24 — CSV import/export + JSON importer + formula-injection hardening

**Phase 1. Depends on: CRB-21, CRB-22.**

Port `csv_io.py` and `importer.py`. Source of truth: those files plus `tests/test_csv_io.py`,
`test_importer.py`, and the CSV formula-injection note in `docs/SECURITY_REVIEW.md`.

## Deliverables (in `src/server/csv/`)
- `exportClientsCsv(clients)` — header exactly `name,company,email,status,engagement_type`;
  one row per client; round-trip stable with the importer.
- `importClientsCsv(text)` — parse + validate each row via `parseClient` (CRB-21). Throw
  `ValidationError` on a wrong header, wrong column count, or any invalid value.
- `ClientImporter` — repository-aware importer accepting **CSV or JSON**, collecting
  **per-row errors** (row index + message) instead of failing fast, and adding the valid rows.
  Mirror the Python `ClientImporter` result shape (imported count + errors list).
- **Formula-injection hardening on export:** if a cell value starts with `= + - @` (or tab/CR),
  prefix it with a single quote `'` so spreadsheets don't execute it. Document this in the worklog.

## Tests
- `tests/unit/server/csv.test.ts` — header validation, column-count errors, per-row error
  collection, JSON path, export→import round-trip, and formula-injection escaping
  (e.g. a name `=cmd()` exports as `'=cmd()`).

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-24.md` per conventions.
