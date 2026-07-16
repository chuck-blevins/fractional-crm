# CRB-22 — Clients JSON API (CRUD + status transition)

**What was built**
`web/errors.py` (404/422/409 helpers), `web/routers/clients.py` (Pydantic ClientIn/Out/StatusIn +
6 endpoints over the existing Client domain + SqliteClientRepository), and `web/app.py` now includes
the clients router. Domain errors map to HTTP: ValueError→422 (invalid) / 409 (duplicate on add),
KeyError→404.

**How it was built (the loop)**
- Claude scaffolded `test_clients_api.py` (11 cases, red).
- qwen2.5-coder-7b via Aider: FAILED twice — first with a pseudocode contract, then even with exact
  valid Python, aider did not apply the multi-file whole-format edits (files stayed 0 bytes).
- LAST RESORT (per the loop rule): reviewer authored the four files directly. Both failures + the
  decomposition recommendation are recorded in `.agent/lessons.md`.

**Finding**
The local 7B handles single-file tool/function stories (CRB-20, CRB-21) but not a multi-file, multi-
endpoint router in one aider run. Future router stories should be split into separate runs or authored
by the reviewer until a stronger local model is in place.

**Test coverage**
- `test_clients_api.py`: create/get/list, 404 missing, 409 duplicate, 422 invalid email, update (+404),
  delete (+404), allowed vs disallowed status transition. Full suite 218 green.
