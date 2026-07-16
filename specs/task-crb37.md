# CRB-37 — Remove Python app; rewrite docs for the web app

**Phase 5 (cleanup). Depends on: all prior stories reaching parity.**

Once CRB-21…CRB-36 have ported and verified every behavior, remove the Python implementation so
the repo is a clean TypeScript web app deployable from `main`.

## Preconditions (verify before deleting anything)
- Every Python module under `src/fractional_crm/` has a TS equivalent whose ported tests are green.
- The TS test suite (`pnpm test`) and e2e (`pnpm test:e2e`) pass.
- Cross-check the parity table in `docs/worklog/CRB-37.md` (module → TS location → test file).

## Deliverables
- Delete `src/fractional_crm/`, the Python `tests/test_*.py`, `pyproject.toml`, `.coverage`,
  `.pytest_cache/`, and Python entries from `.gitignore`.
- Rewrite `README.md` and `docs/USAGE.md` for the web app (setup with pnpm, env vars, `pnpm dev`,
  Postgres via docker-compose, running tests, deploy pointer to Nexlayer).
- Keep `docs/SECURITY_REVIEW.md` but add a short "TS migration" addendum noting where each control
  now lives (email validation, CSV formula-injection escaping, auth).
- `docs/worklog/CRB-37.md`: the full parity table + confirmation the suites pass.

## Definition of Done
- Repo builds and tests green with no Python present; `pnpm build` succeeds.
- Annotation + worklog per conventions. (Deployment/Nexlayer config is handled separately, post-migration.)
