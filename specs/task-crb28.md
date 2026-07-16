# CRB-28 — API: Interactions (log + list newest-first)

**Linear:** [CRB-28](https://linear.app/crbc/issue/CRB-28/api-interactions-log-list-newest-first)

**Phase 2. Depends on: CRB-23.**

Persist interactions and expose them per client. Port `interaction.py` / `interaction_log.py`
behavior: `list_for_client` returns **newest first**. Source of truth: `tests/test_interaction.py`.

## Deliverables
- `src/server/interactionService.ts`: `add(input)` (validate via `parseInteraction`, require the
  client to exist → else `NotFoundError`); `listForClient(email)` → newest first (`date desc`,
  then `createdAt desc` as tiebreaker).
- `src/app/api/clients/[email]/interactions/route.ts`: `GET` → `200` newest-first;
  `POST` → `201`, `400` invalid, `404` if client missing.

## Tests
- `tests/unit/api/interactions.test.ts` — create + list ordering (newest first), `400` on bad
  `kind`/empty summary, `404` on unknown client.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-28.md` per conventions.
