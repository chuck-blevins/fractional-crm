# CRB-30 — Clients UI (list / create / edit / status; HTMX)

## What was built
Accessible, server-rendered client management over the existing domain + repository.

- `src/fractional_crm/web/pages_clients.py` (new): gated router at `/clients`.
  - `GET /clients` — table of clients with per-row edit link + status form.
  - `GET /clients/new`, `POST /clients` — create; invalid/duplicate re-renders the form with an
    accessible error summary (200), else redirect to `/clients`.
  - `GET /clients/{email}/edit`, `POST /clients/{email}` — edit (email is the immutable key).
  - `POST /clients/{email}/status` — status transition; invalid transition re-renders unchanged.
  - Every POST supports HTMX (returns the `_table.html` fragment when `HX-Request`) AND a plain
    form POST → 303 redirect. Handlers are sync `def` (sqlite repo is thread-bound).
- `templates/clients/list.html`, `_table.html` (HTMX-swappable fragment), `form.html`
  (create/edit, error summary with `role="alert"` + focus, labelled fields, `readonly` email on edit).
- `client.py`: exposed `ALLOWED_TRANSITIONS` and `STATUSES`/`ENGAGEMENT_TYPES` (pure refactor —
  behaviour unchanged) so the UI drives selects/transitions from the same source the domain enforces.

## Key decisions
- **Status control is domain-driven:** each row offers only `ALLOWED_TRANSITIONS[status]`, so an
  `active` client shows `paused`/`closed` and never `prospect`. No transition rules re-implemented
  in the web layer.
- **Return type `Response`** (not `HTMLResponse | RedirectResponse`) on the POST handlers — a union
  annotation makes FastAPI try to build a response model and errors at import.
- **Progressive enhancement:** forms work with no JS; HTMX returns the table fragment for in-place
  swaps.

## Test coverage (`tests/web/test_clients_ui.py`)
List renders seeded rows; create with a bad email re-renders an error and persists nothing; valid
create redirects and persists; the status form for an `active` client offers `paused`/`closed` but
not `prospect`; a status POST actually transitions the client. Full suite: **267 passed**.

## Build notes (local-LLM loop)
- Both templates (`_table.html`, `form.html`) built by qwen2.5-coder-7b via aider — one-file runs,
  **zero bounces**; the pre-stub → in-place-edit approach again avoided the path-prefix trap.
- Reviewer wrote the router (domain-error glue, HTMX branch), the tests, and the domain refactor.
