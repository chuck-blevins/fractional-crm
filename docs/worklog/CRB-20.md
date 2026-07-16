# CRB-20 — FastAPI app scaffold + health + test harness

**What was built**
The FastAPI web layer entry point over the existing domain: `src/fractional_crm/web/` package with
`create_app() -> FastAPI` (app factory) + a module-level `app`, and a public `GET /health` returning
`{"status": "ok"}`. Dependency manifests (`requirements.txt`, `requirements-dev.txt`).

**Why**
Foundation for every later web story. The health route is public so the Nexlayer container health
check (CRB-35) can reach it before auth (CRB-28) lands.

**How it was built (the loop)**
- Claude scaffolded the failing acceptance test `tests/web/test_health.py` (red).
- qwen2.5-coder-7b (LM Studio @172.31.0.12) via Aider implemented `web/app.py` + `web/__init__.py` → green.
- Reviewer (Claude) added the requirements manifests + this worklog and verified the full suite.

**Lesson recorded** (`.agent/lessons.md`)
With `--auto-test` on a greenfield task, the 7B latched onto the red pytest output and emitted
environment advice for 3 reflections before producing files. Rule added: create new files WITHOUT
`--auto-test`, tiny format-forward message, test after.

**Run**: `uvicorn fractional_crm.web.app:app --reload`

**Test coverage**
- `tests/web/test_health.py` — `GET /health` returns `200 {"status":"ok"}`.
- DoD gate: full `python -m pytest -q` green (existing domain tests + the new web test).
