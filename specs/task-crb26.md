# CRB-26 — API: Engagements CRUD

**Phase 2. Depends on: CRB-22 (and the error helper from CRB-25).**

Expose `engagementService` over route handlers, same conventions as CRB-25.

## Deliverables
- `src/app/api/engagements/route.ts`: `GET` (list; optional `?clientEmail=` filter) → `200`;
  `POST` (create) → `201`, `400` invalid, `404` if the referenced client does not exist,
  `409` on duplicate for that client key.
- `src/app/api/engagements/[id]/route.ts`: `GET` → `200`/`404`; `PUT` → `200`/`400`/`404`;
  `DELETE` → `204`/`404`.
- Reuse `toErrorResponse` and Zod request validation. Enforce `endDate >= startDate` and
  `monthlyRate > 0` via `parseEngagement`.

## Tests
- `tests/unit/api/engagements.test.ts` — happy paths, `400` on `monthlyRate <= 0` and on
  `endDate < startDate`, `404` on unknown client, list filter by `clientEmail`.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-26.md` per conventions.
