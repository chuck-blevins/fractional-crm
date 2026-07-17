# CRB-29 — Base layout + accessible nav (Jinja2)

## What was built
The accessible HTML shell every page renders inside, plus the Jinja2/static plumbing.

- `src/fractional_crm/web/templates.py` (new): shared `Jinja2Templates` env pointed at
  `web/templates/`.
- `src/fractional_crm/web/pages.py` (new): gated UI router. `GET /` renders `index.html`
  (dashboard placeholder). Self-gates via `Depends(require_session)`.
- `src/fractional_crm/web/templates/base.html` (new): `<!doctype html>`, `lang="en"`,
  skip-to-content link, semantic `<header><nav aria-label="Main"><main id="main">`, six
  section links with `aria-current="page"` on the active one, a no-JS logout form, and the
  HTMX script tag. The single `<h1>` is supplied per page via `{% block content %}` (the
  brand is a plain link, not an `<h1>`).
- `src/fractional_crm/web/templates/index.html` (new): dashboard placeholder extending
  `base.html` (widgets arrive in CRB-31).
- `src/fractional_crm/web/static/style.css` (new): readable base, skip-link reveal on focus,
  visible focus outlines (`3px solid #005fcc`), high-contrast link/button colours (~5.9:1),
  horizontal nav, `aria-current` emphasis.
- `app.py`: mounts `/static`, includes the pages router; `/` moved out of `auth.py`.
- `tests/web/conftest.py`: added an `anon_client` fixture (logged-out) alongside `client`.

## Key decisions
- **`/` moved from `auth.py` to a dedicated `pages.py`** so the UI phase (CRB-30+) has a home
  for server-rendered pages; `auth.py` keeps only login/logout + the `require_session` gate.
- **One `<h1>` per page:** the header brand is a link, not a heading — the page's content
  block owns the single `<h1>` (WCAG AA). Caught in review after the model wrapped the brand
  in `<h1>`.
- Nav links point at routes that land in later stories; they 404 until then, which is fine
  for the shell.

## Test coverage (`tests/web/test_layout.py`)
Authenticated `GET /` → 200 with the skip link (`href="#main"`), `<nav>`, `<main id="main">`,
and all six section labels + a `/logout` control; unauthenticated `GET /` still redirects to
`/login` (gating preserved). Full suite: **262 passed**.

## Build notes (local-LLM loop)
- `base.html` and `style.css` both built by qwen2.5-coder-7b via aider, **one-file runs, zero
  bounces** — the 7B reproduced the accessible structure accurately.
- Pre-creating each target as a stub (so aider edits in place) sidestepped the recurring
  path-prefix trap; no stray root files this time.
- Reviewer wrote the Python plumbing (templates/pages/app wiring) + fixed the double-`<h1>`.
