# CRB-22 — Domain layer in TypeScript (validators + status state-machine)

**Linear:** [CRB-22](https://linear.app/crbc/issue/CRB-22/domain-layer-in-typescript-validators-status-state-machine)

**Phase 0. Depends on: CRB-20. This is a pure-function story — the local model's sweet spot.**

Port every Python validation rule to pure TypeScript in `src/domain/`. No I/O, no Prisma —
just types, Zod schemas, and pure functions. Behavior must match `src/fractional_crm/`
and its tests exactly. Source of truth: `client.py`, `engagement.py`, `interaction.py`,
`team.py`, `integration.py`, and `tests/test_client.py`, `test_engagement.py`,
`test_interaction.py`, `test_team.py`, `test_integration.py`, `test_status_transitions.py`.

## Deliverables (in `src/domain/`)
- `errors.ts`: `ValidationError` (maps Python `ValueError`) and `NotFoundError` (maps `KeyError`).
- `email.ts`: `assertValidEmail(email)` / `isValidEmail(email)` — reject empty/whitespace local
  part, empty domain, any whitespace, domain without a dot, TLD < 2 chars. Regex-based
  (see conventions — a naive check fails known cases like `a@.co`, `a b@x.io`).
- `client.ts`: `ClientSchema` (Zod) + `parseClient(input): Client`. Fields: `name` (non-empty
  after trim), `company`, `email` (valid), `status` (ClientStatus), `engagementType`
  (coo/cpo/advisor). Throw `ValidationError` on any invalid field.
- `status.ts`: `transitionClientStatus(current, next)` — allow only the transitions in
  conventions; otherwise throw `ValidationError`. Return the new status.
- `engagement.ts`: `parseEngagement(input)`. `monthlyRate` > 0 (int or float);
  `startDate`/`endDate` are ISO `YYYY-MM-DD` strings **stored verbatim** but validated by
  parsing; if `endDate` present it must be `>= startDate`; `role` in coo/cpo/advisor;
  `status` in proposed/active/completed/cancelled; valid `clientEmail`.
- `interaction.ts`: `parseInteraction(input)`. `kind` in call/email/meeting/note; `date` ISO
  date; `summary` non-empty after trim; valid `clientEmail`.
- `team.ts`: `Team` with `addMember(member)` and `membersWithRole(role)`; `TeamMember` role in
  admin/member/guest. Preserve insertion order (plain array/Map — no OrderedMap equivalents).
- `integration.ts`: `Integration` (provider/status/externalId/lastSyncedAt) with `markSynced(ts)`;
  `IntegrationRegistry` with `connect`/`disconnect`/`get` — `get`/`disconnect` throw
  `NotFoundError` when absent; providers/status from the fixed sets.

## Tests
Ported unit tests under `tests/unit/domain/` — one file per module — covering the same cases
as the Python tests (valid construction, each rejection case, each allowed/denied transition,
`endDate >= startDate`, duplicate/missing registry keys, ordering).

## Definition of Done
- `pnpm test` green for `tests/unit/domain/**`; `pnpm typecheck` + `pnpm lint` clean.
- No dependency on Prisma or Next. Annotation + `docs/worklog/CRB-22.md` per conventions.
