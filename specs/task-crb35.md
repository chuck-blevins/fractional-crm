# CRB-35 — Dockerfile + nexlayer.yaml (SQLite volume) — real deploy config

**Phase E. Depends on: CRB-20. Reviewer/Claude likely finishes — deploy config, not TDD.**

Produce the REAL Nexlayer deploy config, superseding the earlier hallucinated one (PR #13, a Next.js/
Postgres topology with an nginx-static Dockerfile). This is a single Python container + a volume for
the SQLite file.

## Deliverables
- `Dockerfile`: `python:3.12-slim`; install `requirements.txt`; copy `src/`; run
  `uvicorn fractional_crm.web.app:app --host 0.0.0.0 --port 8000`; `EXPOSE 8000`; non-root user.
- `nexlayer.yaml`: one pod `app`, image built from the repo, `servicePorts: [8000]`, env
  `CRM_DB_PATH=/data/crm.db`, and a **persistent volume** mounted at `/data` so the SQLite DB survives
  redeploys. Secrets (`CRM_SESSION_SECRET`, `CRM_PASSCODE_HASH`) set in the Nexlayer dashboard, not committed.
- `.dockerignore` (exclude `.venv`, `__pycache__`, tests, `.git`, `docs`).
- Document the deploy flow in `docs/worklog/CRB-35.md`: build locally, `docker run` smoke test on
  `:8000/health`, then how a `main` merge triggers the Nexlayer deploy (ties to CRB-19/CRB-36).

## Verification (no unit test; prove it runs)
- `docker build` succeeds and a local `docker run -p 8000:8000` responds `200` on `/health`.
  (If Docker is unavailable on the build box, document the exact commands for Chuck to run.)

## Definition of Done
- Config committed; smoke steps documented. `docs/worklog/CRB-35.md` per conventions.
