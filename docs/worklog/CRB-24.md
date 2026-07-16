# CRB-24 — Interactions JSON API

**What was built**
`sqlite_interaction_repository.py` (new SQLite persistence for interactions — none existed;
`add` + `list_for_client` newest-first via `ORDER BY date DESC, id DESC`), `get_interaction_repo`
dependency, and `web/routers/interactions.py` (POST/GET `/api/clients/{email}/interactions`) wired
into the app. POST verifies the client exists (404) and validates via the domain Interaction (422).

**How it was built (the loop)**
- Claude scaffolded `test_interactions_api.py` (5 cases, red).
- qwen2.5-coder-7b via aider, ONE file per run (repo → deps edit → router → app wiring) — all applied,
  and the suite passed on the FIRST full assembly with ZERO bounces. The accumulated lessons (sync
  `def`, keep `@router` decorators, real docstrings) prevented the CRB-23 mistakes from recurring.

**Test coverage**
- `test_interactions_api.py`: log + list newest-first, 404 unknown client, 422 bad kind / empty
  summary, empty list. Full suite green.
