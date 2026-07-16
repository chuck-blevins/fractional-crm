# CRB-21 — Config + SQLite wiring

**What was built**
`web/config.py` (`get_db_path` reading `CRM_DB_PATH`, default `crm.db`) and `web/deps.py`
(`get_client_repo` / `get_engagement_repo` returning the existing SQLite repositories bound to the
configured path). `tests/web/conftest.py` adds a `client` fixture (TestClient on an isolated temp DB),
reused by later web stories.

**Why**
The JSON-API stories (CRB-22+) need repositories wired to a configurable, test-isolatable DB path.

**How it was built (the loop)**
- Claude scaffolded `conftest.py` + `test_wiring.py` (red).
- qwen2.5-coder-7b via Aider implemented `config.py` + `deps.py` — GREEN first try, no `--auto-test`
  (applying the CRB-20 lesson; no stall this time).
- Review gate caught a convention miss: the model copied a literal `# one-line docstring` placeholder
  from the prompt as a comment. Bounced back with a corrected message + recorded a prompting lesson;
  second pass clean.

**Decisions**
- Deps are plain factory functions returning a repo per call (simple + test-friendly). Per-request
  connection closing is deferred to where endpoints use `Depends` (CRB-22+) — acceptable for a
  low-volume personal CRM.

**Test coverage**
- `test_wiring.py`: default vs env path; persistence across repo instances on one path; isolation
  across paths; the `client` fixture serves an isolated empty DB. Full suite 207 green.
