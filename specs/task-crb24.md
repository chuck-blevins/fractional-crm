# CRB-24 — Interactions JSON API (log + list newest-first)

**Phase B. Depends on: CRB-21.**

Expose the existing `Interaction` / `InteractionLog` domain. Persist interactions (extend the
SQLite layer if needed, following the existing repository idioms) and list newest-first.

## Deliverables (in `src/fractional_crm/web/routers/interactions.py`)
- `POST /api/clients/{email}/interactions` body (date, kind, summary) → `201`; `422` on invalid
  (bad kind, empty summary, bad date); `404` if the client does not exist.
- `GET /api/clients/{email}/interactions` → `200`, **newest first** (matching
  `InteractionLog.list_for_client`).
- Reuse `web/errors.py`.

## Tests
- `tests/web/test_interactions_api.py`: create + list ordering (newest first), `422` on bad
  `kind`/empty summary, `404` on unknown client.

## Definition of Done
- `python -m pytest -q` green. Docstrings + `docs/worklog/CRB-24.md` per conventions.
