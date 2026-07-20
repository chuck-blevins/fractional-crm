# CRB-36 — GitHub Actions CI (pytest gate)

Phase E. Adds the automated half of the review gate: every PR to `main` (and every push to
`main`) must pass the full test suite. Pairs with Claude's manual review + the CRB-35 deploy config.

## Deliverable
- **`.github/workflows/ci.yml`** — on `pull_request` and `push` to `main`, `ubuntu-latest`,
  Python 3.12 (pip cached on `requirements-dev.txt`), `pip install -r requirements-dev.txt`,
  then `python -m pytest -q`.

## Notes
- The suite is self-contained in CI: the root `tests/conftest.py` sets `CRM_ENV=test`, so no
  real secrets (`CRM_SESSION_SECRET`, `CRM_PASSCODE_HASH`) are needed to run the tests.
- `requirements-dev.txt` pulls in `-r requirements.txt` plus `pytest` + `httpx`; the only test-only
  helper, `tests/web/htmlcheck.py`, uses stdlib `html.parser`, so nothing else to install.

## How this pairs with deploy (CRB-19 / CRB-35)
Green CI → human review → merge to `main` → Nexlayer builds the image from `main`
(`Dockerfile` + `nexlayer.yaml` from CRB-35) and deploys, with secrets set in the Nexlayer
dashboard. CI is the gate that makes "deployable via main-branch merges" trustworthy: main stays
green, so what Nexlayer builds is always a passing tree.

## Verification
- Workflow is valid YAML; runs pytest. Confirm the check goes green on this PR.
