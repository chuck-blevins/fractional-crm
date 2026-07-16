# CRB-30 — Clients UI (list / create / edit / status; HTMX)

**Phase D. Depends on: CRB-22, CRB-29.**

Accessible server-rendered client management. Forms work without JS; HTMX enhances add/edit to
avoid full-page reloads.

## Deliverables
- `GET /clients` — page listing clients (name, company, email, status, engagement type) in a
  `<table>` with a caption/headers. Reuses the Clients API layer or repo directly (server-side).
- Create + edit forms with a `<label>` per field and enum `<select>`s. On submit, re-validate via the
  domain; on error re-render the form with an accessible error summary (focus moved to it). HTMX posts
  return the updated row/list fragment; a non-JS submit does a normal POST→redirect.
- Status control offering ONLY the allowed next transitions for the current status (drive from the
  same allowed-transition set the domain enforces); posts to the status endpoint.

## Tests
- `tests/web/test_clients_ui.py`: `GET /clients` renders seeded rows; POST create with a bad email
  re-renders with an error and does not persist; the status form for an `active` client offers
  `paused`/`closed` but not `prospect`.

## Definition of Done
- `python -m pytest -q` green. Docstrings/comments + `docs/worklog/CRB-30.md` per conventions.
