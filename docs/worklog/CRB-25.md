# CRB-25 — Teams + Integrations JSON API

**What was built**
Two new SQLite repos (`sqlite_team_repository.py` with teams + team_members tables and a
`UNIQUE(team_id,email)` constraint; `sqlite_integration_repository.py` keyed by provider), two deps,
and two routers: `/api/teams` (create, list, add member, list members with `?role=` filter) and
`/api/integrations` (list, connect, disconnect=delete, sync). Error mapping 422/409/404 throughout.

**How it was built (the loop — biggest story, 6 files)**
- Built by qwen2.5-coder-7b via aider, one file per run (2 repos → deps → 2 routers → app wiring).
- One review-gate catch: qwen emitted the integration-repo filename WITHOUT the `src/fractional_crm/`
  prefix, so aider wrote it to the repo root and left the intended path empty (and `ast.parse("")`
  falsely "passed"). Reviewer relocated the file; lesson recorded (verify non-empty at the intended
  path via `wc -l`, not ast-parse). No code was ghostwritten — the generated code was correct, just
  misplaced.

**Test coverage**
- `test_teams_api.py` (6) + `test_integrations_api.py` (7): team create/list, member add/list/role
  filter, duplicate 409, bad role 422, unknown team 404; integration connect/list, duplicate 409, bad
  provider 422, disconnect (+404), sync (+404). Full suite green.
