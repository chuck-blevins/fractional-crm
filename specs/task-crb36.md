# CRB-36 — UI: Teams + Integrations

**Linear:** [CRB-36](https://linear.app/crbc/issue/CRB-36/ui-teams-integrations)

**Phase 4. Depends on: CRB-29, CRB-32.**

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
- Annotation + `docs/worklog/CRB-36.md` per conventions.
