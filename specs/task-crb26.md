# CRB-26 — API: Clients CRUD + status transitions

**Linear:** [CRB-26](https://linear.app/crbc/issue/CRB-26/api-clients-crud-status-transitions)

**Phase 2. Depends on: CRB-23.**

Expose `clientService` over App Router route handlers. Establish the shared error-mapping
helper all later API stories reuse.

## Deliverables
- `src/lib/apiError.ts`: `toErrorResponse(err)` — `ValidationError` → `400`,
  `NotFoundError` → `404`, anything else → `500`; body `{ error: string }`. Never leak stack traces.
- `src/app/api/clients/route.ts`: `GET` (list) → `200 [Client]`; `POST` (create) → `201 Client`,
  `400` on invalid, `409` on duplicate email (map the duplicate `ValidationError` to 409 here).
- `src/app/api/clients/[email]/route.ts`: `GET` → `200`/`404`; `PUT` (update) → `200`/`400`/`404`;
  `DELETE` → `204`/`404`.
- `src/app/api/clients/[email]/status/route.ts`: `POST { next }` → `200 Client` on an allowed
  transition, `400` on a disallowed one (unchanged status), `404` if missing.
- Request bodies validated with Zod before hitting the service.

## Tests
- `tests/unit/api/clients.test.ts` — invoke the handlers directly with mock `Request`s against
  the test DB: list/create/get/update/delete happy paths, `400` invalid, `409` duplicate,
  `404` missing, allowed vs disallowed status transition.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-26.md` per conventions.
