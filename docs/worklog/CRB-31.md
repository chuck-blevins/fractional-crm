# CRB-31 — Engagements UI + dashboard reporting widgets

Phase D. First story where the local model was asked to write a **router by analogy**, not just
templates — the experiment Chuck approved.

## What was built
- **`web/pages_engagements.py`** (new): gated `/engagements` router — list (filterable by
  `?client_email=`), create, edit. Keyed by `client_email` (one engagement per client), mirroring
  the Clients UI. Sync `def`; HTMX returns the `_table.html` fragment, else POST→303. Domain
  `ValueError` re-renders the form accessibly; `KeyError` → 404.
- **`templates/engagements/{list,_table,form}.html`**: accessible table (scoped headers, caption,
  em-dash for a null end date), create/edit form with role/status `<select>`s driven from the
  domain, `role="alert"` error summary that takes focus, optional end date.
- **Dashboard widgets on `/`** (fill the CRB-29 slots): active-engagement count and monthly
  run-rate, currency-formatted (`$5,000`, `$0` when none), behind `data-testid` hooks.
- **`engagement.py`**: exposed `ROLES` / `STATUSES` public constants (pure refactor, same pattern
  as CRB-30) so the UI drives selects from the domain.
- **`pages.py`**: dashboard handler computes the reporting summary and passes it to the template
  (reviewer glue).

## Test coverage (`tests/web/test_engagements_ui.py`, 8 tests)
List renders + client filter; create rejects `monthly_rate<=0` and `end_date<start_date`
accessibly (200, not persisted); valid create redirects and persists; new-form selects limited to
domain enums; dashboard shows the active count and `$`-formatted run-rate ($0 when none).
**Full suite: 289 passed.**

## Build notes (local-LLM loop) — the experiment
**Router by analogy — WORKED, 1 bounce.** Given `pages_clients.py` as the reference and the
differences as prose (keyed by client_email, `monthly_rate: float`, `end_date or None`, no
status-transition route, `?client_email=` filter), qwen adapted the entire pattern correctly on the
first pass — imports, enum wiring, try/except structure, HTMX branch, 404 handling. The **one** bug
was a wiring gap: it threaded the new `client_email` filter into `_rows()` and into the handler's
call, but forgot to add the parameter to the `_list_response()` helper in between, so every list
request raised `TypeError`. Fixed with a one-function bounce (exact replacement supplied). This is
the known ceiling in a new place: strong drafter, misses the last mechanical thread-through.
**Verdict: the local loop can extend an existing pattern to a new model, not just fill templates.**

**Templates — 3 of 4 clean; `_table.html` needed a scaffold fix (see lessons.md).** form.html,
list.html and the dashboard built first try. `_table.html` silently no-op'd **twice**: qwen wrote
the correct markup but labelled its output fence `base.html`, because the reviewer's stub for it
wrongly began `{% extends "base.html" %}` — a fragment must not — which pulled base.html into
aider's repo-map and gave the model a wrong filename to latch onto. No stray at repo root, no
"Applied edit" line, just aider asking to "add base.html to the chat". Fixing the stub (no extend,
minimal) made the same prompt apply cleanly. Root cause was reviewer-side, not the model.
