# CRB-33 — Teams + Integrations UI

**Phase D. Depends on: CRB-25, CRB-29.**

## Deliverables
- `GET /teams`: list teams; view a team's members; add-member form (role `<select>`
  admin/member/guest); duplicate `(team,email)` surfaced as an accessible inline error.
- `GET /integrations`: list the fixed providers (slack/github/gitlab/figma/intercom/zendesk) with
  status; connect (enter external_id), disconnect, and "sync now" (shows `last_synced`). HTMX for the
  toggles; non-JS forms still work.

## Tests
- `tests/web/test_teams_ui.py`: add member happy path + duplicate error; role select limited to allowed set.
- `tests/web/test_integrations_ui.py`: connect/disconnect toggles status; sync updates the last-synced label.

## Definition of Done
- `python -m pytest -q` green. Docstrings/comments + `docs/worklog/CRB-33.md` per conventions.
