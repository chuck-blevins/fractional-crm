# CRB-34 — CSV import/export UI

Phase D. Adds CSV/JSON import + export to the existing `/clients` page, on top of the
already-tested CSV API layer (CRB-27). No new resource — a route and a template block.

## What was built
- **`web/pages_clients.py`** — new gated `POST /clients/import` handler
  (`import_clients_from_upload`). Reads the uploaded file, enforces a 5 MiB limit, UTF-8-decodes,
  branches `.json` vs CSV, and runs `ClientImporter`. Every failure mode (too large, non-UTF-8,
  unparseable) **re-renders the clients list with an error summary instead of raising** — so the
  plain form POST always returns readable HTML, never a 500. `_list_response` gained an optional
  `import_result` passthrough so the same list template renders the post-import summary.
- **`templates/clients/list.html`** — an "Import / export" section: an **Export CSV** link to
  `GET /api/clients/csv/export`; a multipart import `<form>` with a label-bound file input
  (`accept=".csv,.json"`) that disables its submit + sets `aria-busy` on submit (the spec's
  "controls disabled while in flight", as unobtrusive progressive enhancement); and a conditional
  `role="status"` summary showing the imported count (`data-testid="imported-count"`) and a
  per-row error list (`Row N: message`, each `data-testid="import-error"`).

## Test coverage (`tests/web/test_csv_ui.py`, 5 tests)
Export link points at the export endpoint; the import form is a labelled multipart upload; a mixed
good/bad CSV re-renders with the imported count and the failing row reported by number, and the
valid row persists; the rendered summary is valid HTML; a non-UTF-8 upload is handled gracefully
(no 500). **Full suite: 379 passed, 3 skipped.**

## Build notes (local-LLM loop)
Route and template both authored by qwen via aider (route by analogy from `csv_routes.py`, the
guard-heavy body spoon-fed as code). Three defects, all reviewer-fixed — see `.agent/lessons.md`:
1. **Route ordering** — aider appended `POST /import` *below* the existing `POST /{email}`, so
   `/clients/import` was captured by `/{email}` (`email="import"`) and blew up inside
   `update_client`. Relocated the literal route above the parametrized group.
2. **Whole-file collateral damage** — the same run gratuitously rewrote the untouched
   `_form_response`, reverting its `TemplateResponse` to the deprecated old-style call
   (`TypeError: unhashable type: 'dict'`) and renaming context keys, regressing 5 form/validity
   tests while the targeted CRB-34 tests passed. Caught only by the FULL suite; reverted the hunk.
3. **Dropped `File` import** — added `UploadFile` but not `File`; reviewer-added.

Reinforced practice: after a whole-file aider edit of a multi-function file, diff the entire file
and revert anything outside scope, and always run the full suite — the targeted run looked done at
each step while two regressions hid outside it.
