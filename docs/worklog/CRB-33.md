# CRB-33 — Teams + integrations UI

Phase D. Third and fourth stories where the local model wrote a **router by analogy**
(the CRB-31/32 method), covering two resources in one branch: team management and provider
integrations. Resumed from a working tree the 2026-07-18 session had built but never committed.

## What was built

### Teams (`web/pages_teams.py` + `templates/teams/`)
- **Router**: gated `/teams`. `GET /teams` lists teams; `POST /teams` creates one; `GET /teams/{id}`
  renders the detail page with its member roster; `POST /teams/{id}/members` adds a member. Sync
  `def` (thread-bound sqlite repo). Domain `ValueError` (blank name / bad member field) re-renders
  the page at 200 with entered values preserved; unknown team → 404. HTMX add-member gets the
  `_roster.html` fragment back; non-HTMX gets a 303 redirect. Role `<select>` driven from the domain
  `ROLES` tuple, never re-encoded in the template.
- **Templates**: `list.html` (create form + team list), `detail.html` (single `<h1>`, member roster,
  label-bound add-member form with the domain-driven role select), `_roster.html` (HTMX-swappable
  member fragment).

### Integrations (`web/pages_integrations.py` + `templates/integrations/`)
- **Router**: gated `/integrations`. `GET /integrations` lists **every** provider — connected or not —
  so the page always shows the full catalog with per-row state. `POST /integrations/connect` connects
  a provider (validates provider + external id); `POST` disconnect removes one; `POST` sync stamps
  `last_synced_at` from the **server clock** (injectable, pinned in tests). Unknown provider → 404;
  blank external id / unknown / already-connected provider re-render accessibly at 200. HTMX connect
  and sync return the `_table.html` fragment.
- **Templates**: `list.html` (error region + provider table + connect form with the domain
  `PROVIDERS`-driven select), `_table.html` (one row per provider keyed by `data-testid`, showing
  status / account / last-synced with a placeholder when never synced).

Both routers drive their selects from public domain constants — `team.ROLES` and
`integration.PROVIDERS` / `STATUSES` were exposed via a pure refactor (private aliases kept).

## Test coverage
- `tests/web/test_teams_ui.py` (17 fns incl. one parametrized) — list/empty/links, create +
  redirect, **stripped-name persistence**, blank-name re-render, detail + roster, unknown-team 404,
  domain-limited role select, add-member persist/duplicate/invalid/unknown-team, HTMX roster
  fragment, full-page HTML validity.
- `tests/web/test_integrations_ui.py` (18 fns) — full provider catalog shown, un/connected states,
  domain-limited provider select, connect persist/redirect, blank/unknown/already-connected
  re-renders, disconnect, clock-pinned sync + label + never-synced placeholder, unknown-provider
  404s, HTMX connect/sync fragments, non-JS forms, full-page HTML validity.
- **Full suite: 374 passed, 3 skipped.**

## Build notes (local-LLM loop)
**Routers by analogy — worked again** (third/fourth confirmation). Fed the nearest existing
`pages_*.py` as `--read` with the contract as prose+signatures; qwen reproduced the router pattern
for both resources.

**Teams-router review: three findings, two aider bounces, both hit the known 7B ceiling.**
1. *Docstrings* missing on the three `_response` helpers — added via aider.
2. *`create_team` persisted the raw form value.* `Team(name)` validates and strips but its return
   was discarded, so `repo.create_team(name)` stored `"  Platform  "` with whitespace. Pinned first
   with a new red test (`test_create_team_persists_stripped_name`), then fixed to persist
   `Team(name).name`. **First bounce dropped the surrounding `try/except`** when the prompt quoted
   only the two interior lines — regressing the (previously green) blank-name test into an uncaught
   500. Re-bounced quoting the **entire function** as code; landed clean. New lessons.md rule:
   quote the whole enclosing block when an edit lives inside defensive control flow.
3. *Leaked `# Add this import` prompt comment.* The 7B ignored this delete on **both** runs (it lands
   ~1 edit-intent per run and drops extras) — reviewer-finished the one-token deletion via `sed`
   (cleanup, last resort, recorded).

**Recovery note:** the entire 07-18 build sat uncommitted in the code_vm working tree; it was
recovered intact, verified green, and squashed into a single `feat(CRB-33)` commit atop the red
scaffold. Landed bottom-up behind CRB-32 (PR #35) per the stacked-PR rule — plain merges, no
`--delete-branch` until the stack tip is on main.
