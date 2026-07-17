# CRB-32 — Interactions timeline UI

**Phase D. Depends on: CRB-24, CRB-29.**

## Deliverables
- On the client detail page, an interactions timeline (newest first) from the interactions API,
  as an ordered list grouped/sorted by date with accessible date/kind labelling.
- A "log interaction" form (kind `<select>`: call/email/meeting/note; date; required summary). HTMX
  prepends the new entry on success; non-JS submit does POST→redirect. Empty state when none.

## Tests
- `tests/web/test_interactions_ui.py`: timeline renders newest-first; empty summary re-renders with an
  accessible error and does not persist.

## Definition of Done
- `python -m pytest -q` green. Docstrings/comments + `docs/worklog/CRB-32.md` per conventions.
