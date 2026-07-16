# CRB-36 — UI: CSV import / export

**Phase 4. Depends on: CRB-29, CRB-31.**

## Deliverables
- On the Clients page: an **Export CSV** button (downloads from `/api/clients/export`) and an
  **Import** dialog that uploads a CSV/JSON file to `/api/clients/import`.
- After import, show a result summary: imported count + a per-row error list (row number + message).
- Disable the controls while a request is in flight; handle oversize/malformed uploads gracefully.

## Tests
- `tests/unit/ui/csv.test.tsx` — import dialog renders the returned per-row errors from a mocked
  response; export button triggers a download request.
- `e2e/csv.spec.ts` — import a small CSV, see the imported clients appear in the list.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-36.md` per conventions.
