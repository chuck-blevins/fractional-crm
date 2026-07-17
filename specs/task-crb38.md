# CRB-38 — Accessibility pass (WCAG 2.1 AA audit + fixes)

**Phase E. Depends on: the UI stories (CRB-29…CRB-34).**

A dedicated pass to hold the UI to WCAG 2.1 AA, rather than trusting it emerged for free.

## Deliverables
- Audit every page for: one `<h1>` + logical heading order; every control labelled; keyboard
  operability (tab order, focus visible, no keyboard traps); `aria-current` on nav; error summaries
  linked to fields; colour contrast ≥ 4.5:1 (text) / 3:1 (large); images have alt text; forms usable
  without JS.
- Fix the gaps found. Record the audit (page → issues → fixes) in `docs/worklog/CRB-38.md`.
- Add automated checks where cheap: a pytest that asserts key landmarks/labels on each main page; if
  feasible, an `axe-core` check via Playwright (optional — only if it doesn't drag in heavy tooling).

## Definition of Done
- Audit complete with fixes; `python -m pytest -q` green. `docs/worklog/CRB-38.md` per conventions
  documents the AA checklist and outcomes.
