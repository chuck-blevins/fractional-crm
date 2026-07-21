# CRB-41 — Import / Export page (`/import-export`)

## What
A dedicated `/import-export` page that gives the existing CSV features a home off the nav:
a download link for the export endpoint and an accessible upload form for the import handler.
Closes the dead Import/Export nav link found during the 2026-07-21 go-live sweep (the CRB-34
CSV UI shipped only as controls embedded on the `/clients` page).

## Why
The nav promised an Import/Export destination; the feature existed only inline on `/clients`.
This page surfaces both directions in one place without duplicating any logic.

## Key decisions
- **Reuse the existing endpoints, add no new ones.** Export is a link to
  `GET /api/clients/csv/export`; import posts to the existing `POST /clients/import` handler
  (which already re-renders the clients list with a per-row import summary and never 500s on a
  bad file). The page is a thin, static shell — no repository dependency.
- **Sync `def` handler, no per-route auth** — gating is applied once at include time in `app.py`.
- **Accessible import form** — `enctype="multipart/form-data"`, a `<label for="file">` bound to
  the `<input type="file" id="file" name="file" required>`, works without JS.

## Files
- `src/fractional_crm/web/pages_import_export.py` — new page router (`GET /import-export`).
- `src/fractional_crm/web/templates/import_export/index.html` — new template.
- `src/fractional_crm/web/app.py` — wire `import_export_pages_router` (gated include).

## Tests
- `tests/web/test_import_export_page_ui.py` — page 200; export link present; accessible import
  form (action/enctype/method/file input/label); valid HTML.
- Full suite: 390 passed, 3 skipped.

## Build
Local Qwen-7B via aider, one file per run (template + router by analogy to
`pages_teams.py`/`teams/list.html`); app.py wiring done as a separate reviewer edit.
