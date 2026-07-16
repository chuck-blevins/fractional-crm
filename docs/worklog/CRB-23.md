# CRB-23 — Engagements JSON API

**What was built**
`web/routers/engagements.py` (EngagementIn/Out + CRUD keyed by client_email, with `?client_email=`
filter on list) wired into `create_app()`. Domain errors map to 422/409/404. Spec adjusted from the
original CRB-23 draft: the engagement repo is keyed by **client_email** (one engagement per client),
not an `id`.

**How it was built (the loop — first genuine multi-bounce story)**
- Built by qwen2.5-coder-7b via aider on a HEALTHY .12 box (the earlier "router" failures were the
  wedged endpoint, not the model — see lessons). One file per aider run + separate app.py wiring run.
- Three review-gate bounces, each fixed by a tighter spec (no ghostwriting):
  1. `async def` endpoints used the thread-bound sqlite repo across threads → ProgrammingError. Fixed to
     sync `def`.
  2. Missing docstrings; list filter used `repo.get()` (500 on miss) instead of a comprehension.
  3. The rewrite dropped all `@router.*` decorators (blanket 404s) → restored with exact decorators.
- Test strengthened with `test_filter_no_match_returns_empty` to lock in the filter fix.

**Test coverage**
- `test_engagements_api.py` (10): create/get, list + filter (+ empty on miss), 404 missing, 409 dup,
  422 rate<=0 and end<start, update (+404), delete (+404). Full suite green.
