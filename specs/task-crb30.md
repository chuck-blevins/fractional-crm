# CRB-30 — API: CSV import/export endpoints

**Linear:** [CRB-30](https://linear.app/crbc/issue/CRB-30/api-csv-importexport-endpoints)

**Phase 2. Depends on: CRB-25, CRB-26.**

Wire the CSV/JSON import + export from CRB-25 to HTTP.

## Deliverables
- `src/app/api/clients/export/route.ts`: `GET` → `200` with `Content-Type: text/csv` and
  `Content-Disposition: attachment; filename="clients.csv"`; body from `exportClientsCsv`
  (formula-injection escaping already applied).
- `src/app/api/clients/import/route.ts`: `POST` (multipart file **or** raw CSV/JSON body) →
  `200 { imported, errors }` using `ClientImporter`. Malformed uploads → `400`.
- Cap upload size (reject > 5 MB with `413`).

## Tests
- `tests/unit/api/clients-csv.test.ts` — export headers + body, import with a mixed valid/invalid
  payload returning per-row errors, round-trip (export then re-import), oversize `413`.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-30.md` per conventions.
