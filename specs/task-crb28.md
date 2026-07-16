# CRB-28 — API: Teams + Integrations

**Phase 2. Depends on: CRB-22.**

Persist and expose Teams/TeamMembers and Integrations. Port `team.py` and `integration.py`.
Source of truth: `tests/test_team.py`, `test_integration.py`.

## Deliverables
- `src/server/teamService.ts`: create team; `addMember` (role in admin/member/guest; reject
  duplicate `(teamId,email)` with `ValidationError`); `membersWithRole(teamId, role)`.
- `src/server/integrationService.ts`: `connect(input)` (provider/status from fixed sets;
  reject duplicate provider); `disconnect(provider)` and `get(provider)` → `NotFoundError` if
  absent; `markSynced(provider, ts)` sets `lastSyncedAt` and `status="connected"`.
- Route handlers:
  - `src/app/api/teams/route.ts` (`GET`/`POST`), `src/app/api/teams/[id]/members/route.ts` (`GET`/`POST`).
  - `src/app/api/integrations/route.ts` (`GET`/`POST` connect),
    `src/app/api/integrations/[provider]/route.ts` (`GET`/`DELETE`),
    `src/app/api/integrations/[provider]/sync/route.ts` (`POST` markSynced).
- Reuse `toErrorResponse` + Zod.

## Tests
- `tests/unit/api/teams.test.ts` and `integrations.test.ts` — member roles + duplicate rejection;
  connect/get/disconnect/markSynced, `404` on unknown provider, enum rejection.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-28.md` per conventions.
