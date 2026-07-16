# CRB-33 — UI: Clients (list / create / edit / status)

**Linear:** [CRB-33](https://linear.app/crbc/issue/CRB-33/ui-clients-list-create-edit-status)

**Phase 4. Depends on: CRB-26, CRB-32.**

## Deliverables
- `src/app/(dashboard)/clients/page.tsx`: table of clients (name, company, email, status,
  engagement type) from `GET /api/clients`.
- Create + edit forms (client component) posting to the Clients API; inline field validation that
  mirrors the domain rules (email, required name, enum selects). Server errors surfaced per-field.
- A status control that only offers **allowed** next transitions for the current status
  (drive it from the same transition map as `src/domain/status.ts`) and calls the status endpoint.
- Optimistic or post-refresh list update; loading + error states.

## Tests
- `tests/unit/ui/clients.test.tsx` (RTL) — renders rows from a mocked fetch; submitting an invalid
  email shows an inline error and does not call the API; the status control hides disallowed transitions.
- `e2e/clients.spec.ts` — create a client, see it in the list, move it `active → paused`.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-33.md` per conventions.
