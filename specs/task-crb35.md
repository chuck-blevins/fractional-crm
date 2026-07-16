# CRB-35 — UI: Interactions timeline per client

**Linear:** [CRB-35](https://linear.app/crbc/issue/CRB-35/ui-interactions-timeline-per-client)

**Phase 4. Depends on: CRB-28, CRB-32.**

## Deliverables
- On the client detail view, a timeline of interactions (newest first) from
  `GET /api/clients/[email]/interactions`, grouped/sorted by date.
- A "log interaction" form (kind select: call/email/meeting/note; date; summary required)
  posting to the interactions endpoint; the new entry appears at the top on success.
- Empty state when a client has no interactions.

## Tests
- `tests/unit/ui/interactions.test.tsx` — timeline renders newest-first from a mocked fetch;
  empty summary is rejected inline.
- `e2e/interactions.spec.ts` — log an interaction; it appears at the top of the timeline.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-35.md` per conventions.
