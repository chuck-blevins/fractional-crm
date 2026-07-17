# CRB-29 — Base layout + accessible nav (Jinja2)

**Phase D. Depends on: CRB-28. Scaffold a template-assertion test to keep the model on-rails.**

The accessible HTML shell every page renders inside. Target WCAG 2.1 AA (see conventions).

## Deliverables
- Jinja2 configured in the app; templates under `src/fractional_crm/web/templates/`,
  static CSS under `src/fractional_crm/web/static/`.
- `templates/base.html`: `<!doctype html>`, `lang="en"`, a skip-to-content link, semantic
  `<header><nav><main id="main">`, one `<h1>` block per page, and the HTMX script tag.
- Accessible `<nav>` linking Clients, Engagements, Interactions, Teams, Integrations, Import/Export,
  and a logout control. Current page marked `aria-current="page"`.
- `GET /` renders a dashboard placeholder (widgets slotted in CRB-31) extending `base.html`.
- Minimal CSS: readable defaults, visible focus outline, adequate contrast.

## Tests
- `tests/web/test_layout.py`: `GET /` (authenticated) returns `200`; response HTML contains the skip
  link, a `<nav>`, `<main id="main">`, and all six nav links.

## Definition of Done
- `python -m pytest -q` green. Docstrings/comments + `docs/worklog/CRB-29.md` per conventions.
