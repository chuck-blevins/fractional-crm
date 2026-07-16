# CRB-22 — Repository/service layer over Prisma (clients, engagements)

**Phase 1. Depends on: CRB-20, CRB-21.**

Port the Python repository semantics to Prisma-backed services. The Python interface is
`add / get / list / update / delete`; `add` raises on duplicate key, the rest raise when the
key is missing. Source of truth: `repository.py`, `sqlite_repository.py`, and
`tests/test_repository.py`, `test_sqlite_repository.py`.

## Deliverables (in `src/server/`)
- `clientService.ts`:
  - `add(input)` — validate via `parseClient` (CRB-21), then create. Throw `ValidationError`
    if a client with that `email` already exists (map Python duplicate-key `ValueError`).
  - `get(email)` — throw `NotFoundError` if absent.
  - `list()` — all clients, stable order (createdAt asc).
  - `update(input)` — throw `NotFoundError` if absent; re-validate.
  - `delete(email)` — throw `NotFoundError` if absent.
  - `transitionStatus(email, next)` — load, apply `transitionClientStatus` (CRB-21), persist.
- `engagementService.ts`: same shape, keyed by `clientEmail`; validate via `parseEngagement`.
- All DB access through the `src/lib/prisma.ts` singleton. Services are pure of HTTP concerns.

## Tests
- `tests/unit/server/clientService.test.ts` and `engagementService.test.ts` — integration tests
  against the docker Postgres (or a per-test schema), covering: add/get/list/update/delete,
  duplicate-key rejection, missing-key `NotFoundError`, and a full status-transition round-trip.
  Use a `beforeEach` truncate so tests are isolated. (A DB is required — see CRB-20 compose.)

## Definition of Done
- `pnpm test` green with the test DB up; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-22.md` per conventions.
