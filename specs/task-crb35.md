# CRB-35 — UI: Teams + Integrations

**Phase 4. Depends on: CRB-28, CRB-31.**

## Deliverables
- `src/app/(dashboard)/teams/page.tsx`: list teams; view a team's members; add a member
  (role select admin/member/guest); duplicate `(team,email)` surfaced as an inline error.
- `src/app/(dashboard)/integrations/page.tsx`: list the fixed providers
  (slack/github/gitlab/figma/intercom/zendesk) with connection status; connect (enter externalId),
  disconnect, and "sync now" (calls markSynced, shows `lastSyncedAt`).

## Tests
- `tests/unit/ui/teams.test.tsx` — add member happy path + duplicate error; role select limited to
  the allowed set.
- `tests/unit/ui/integrations.test.tsx` — connect/disconnect toggles status; sync updates the
  last-synced label.
- `e2e/integrations.spec.ts` — connect a provider, then disconnect it.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-35.md` per conventions.
