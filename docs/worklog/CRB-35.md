# CRB-35 — Dockerfile + nexlayer.yaml (real deploy config)

Phase E. Produces the REAL Nexlayer deploy config, superseding the hallucinated PR #13
(a Next.js/Postgres topology with an nginx-static Dockerfile). The app is a single Python
container: FastAPI served by uvicorn, SQLite persisted on a mounted volume.

## Deliverables
- **`Dockerfile`** — `python:3.12-slim`, installs `requirements.txt`, copies `src/`, runs
  `uvicorn fractional_crm.web.app:app --host 0.0.0.0 --port 8000`, `EXPOSE 8000`, non-root
  `appuser` (uid 10001). Sets `PYTHONPATH=/app/src` (src-layout — see finding below),
  `CRM_ENV=production`, `CRM_DB_PATH=/data/crm.db`. Includes a `/health` HEALTHCHECK.
- **`nexlayer.yaml`** — one pod `app`, `path: /`, `servicePorts: [8000]`, a 1Gi volume mounted at
  `/data`, and non-secret `vars` (`CRM_ENV`, `CRM_DB_PATH`). **Validated with
  `nexlayer_validate_yaml` → VALID** (only warning: no `url` ⇒ preview deployment).
- **`.dockerignore`** — excludes `.venv`, `__pycache__`, tests, docs, specs, `.agent`, `.git`, `*.db`.

## Key findings (verified on the box)
- **src-layout needs `PYTHONPATH=/app/src`.** A bare `uvicorn fractional_crm.web.app:app` fails with
  `ModuleNotFoundError: fractional_crm` because the package is only on the *pytest* path
  (`pyproject` `pythonpath=["src"]`), not installed. Setting `PYTHONPATH` in the image fixes it.
- **Runtime smoke (uvicorn directly, `PYTHONPATH=src`):** `/health` → 200 `{"status":"ok"}`,
  `/` → 303 → `/login` (gated), `/login` → 200. The exact container command works.
- **`CRM_DB_PATH` drives the DB location** (`web/config.py`, default `crm.db`) — so the `/data`
  volume + `CRM_DB_PATH=/data/crm.db` persists the SQLite file across redeploys.
- **`CRM_ENV=production` is required** — `auth.is_production()` fail-secures, so `session_secret()`
  raises unless `CRM_SESSION_SECRET` is set. Set the two secrets out-of-band (below).

## Secrets (never committed — set in the Nexlayer dashboard)
- `CRM_SESSION_SECRET` — generate: `python -c "import secrets; print(secrets.token_hex(32))"`
- `CRM_PASSCODE_HASH` — the single-user login hash (`<salt_hex>$<digest_hex>`, PBKDF2). Generate from
  the chosen passcode using the app's hasher (`fractional_crm.web.auth`), then paste the value.

## Build + deploy flow (no Docker on either VM — build remotely)
Neither the orchestrator box nor VM1 has Docker, so build via one of:
1. **Nexlayer remote build+deploy** (preferred): sign in to the Nexlayer MCP, then
   `nexlayer_build_and_push_image` (context = repo root, `./Dockerfile`) → put the returned image
   ref in `nexlayer.yaml` → `nexlayer_deploy`. Set the two secrets in the dashboard first.
2. **CI (CRB-36):** GitHub Actions builds + pushes `ghcr.io/chuck-blevins/fractional-crm:latest` on
   merge to `main`, then triggers `nexlayer_deploy` (this is what the committed image ref assumes).
3. **Manual, on any Docker host:**
   ```
   docker build -t fractional-crm:latest .
   docker run -p 8000:8000 -e CRM_ENV=production \
     -e CRM_SESSION_SECRET=... -e CRM_PASSCODE_HASH=... \
     -v crm-data:/data fractional-crm:latest
   curl -s localhost:8000/health   # expect {"status":"ok"}
   ```

## Status
Config committed and YAML-validated. Actual go-live is gated on: (a) Nexlayer sign-in, (b) the two
secrets, (c) an image build (options above). Supersedes PR #13 (close it). Ties to CRB-19 (deploy
issue) and CRB-36 (CI/CD).
