# CRB-36 — GitHub Actions CI (pytest gate on PRs to main)

**Phase E. Depends on: CRB-20. Makes "deployable via main-branch merges" trustworthy.**

Add CI so every PR to `main` must pass the test suite before merge — the automated half of the
review gate.

## Deliverables
- `.github/workflows/ci.yml`: on `pull_request` and `push` to `main`, on `ubuntu-latest`,
  set up Python 3.12, `pip install -r requirements.txt -r requirements-dev.txt`, run
  `python -m pytest -q`. Cache pip.
- (Optional, if time) a lint/format check step.
- Document in `docs/worklog/CRB-36.md` how this pairs with Nexlayer auto-deploy on `main` (CRB-19/35):
  green CI → merge → Nexlayer builds from `main`.

## Verification
- The workflow file is valid YAML and runs pytest. (Confirm the run goes green on the PR that adds it.)

## Definition of Done
- Workflow committed and passing on its own PR. `docs/worklog/CRB-36.md` per conventions.
