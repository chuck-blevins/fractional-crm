# CRB-40 — Global Interactions feed page (`/interactions`)

## What
A standalone `/interactions` page: a global, newest-first feed of every interaction across
all clients. Closes the dead nav link discovered during the 2026-07-21 go-live sweep (the
Interactions nav item pointed at a route that was never built — the CRB-32 interactions UI
only ever lived on each client's detail page as a per-client timeline).

## Why
The base-layout nav promises an Interactions view; only a per-client timeline existed. A
global activity feed is the natural top-level view and what the nav link implied.

## Key decisions
- **New repo read method** `SqliteInteractionRepository.list_all()` — mirrors the existing
  `list_for_client()` but drops the `WHERE client_email=?` filter; same
  `ORDER BY date DESC, id DESC` so ordering is identical to the per-client timeline.
- **Reused the domain/repo** — the page router only reads `repo.list_all()`; no new domain
  logic, no validation in the web layer.
- **Sync `def` handler** (sqlite repos are thread-bound) and **no per-route auth** — gating is
  applied once at include time in `app.py` (`dependencies=[Depends(require_session)]`), the
  house pattern from the security review.
- **Template** extends `base.html`, single `<h1>`, `<ol>` timeline in the `{% if %}` branch and
  the empty-state `<p>` strictly in the `{% else %}` (never nested — the CRB-32 invalid-HTML trap).
  Jinja autoescaping covers the user-supplied summary/email.

## Files
- `src/fractional_crm/sqlite_interaction_repository.py` — add `list_all()`.
- `src/fractional_crm/web/pages_interactions.py` — new page router (`GET /interactions`).
- `src/fractional_crm/web/templates/interactions/index.html` — new template.
- `src/fractional_crm/web/app.py` — wire `interactions_pages_router` (gated include).

## Tests
- `tests/test_interaction_list_all.py` — `list_all()` empty + across-clients newest-first.
- `tests/web/test_interactions_page_ui.py` — page 200; lists across clients newest-first;
  shows client email; empty state; valid HTML (`assert_valid_html`).
- Full suite: 386 passed, 3 skipped.

## Build
Local Qwen-7B via aider, one file per run (repo method, template, router by analogy to
`pages_teams.py`/`teams/list.html`); app.py wiring done as a separate reviewer edit.
