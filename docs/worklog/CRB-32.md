# CRB-32 — Client detail page + interactions timeline

Phase D. Second story where the local model wrote a **router by analogy** (the CRB-31 method),
this time with the reviewer authoring the template prompts as well.

## What was built
- **`web/pages_client_detail.py`**: gated `/clients/{email}` detail router. `GET /{email}` renders
  the client profile plus the interactions timeline; `POST /{email}/interactions` logs one. Sync
  `def` (thread-bound sqlite repo). Two repos injected — the client repo to resolve/404 the client,
  the interaction repo for the timeline. `list_for_client()` already returns newest-first, so the
  router renders in the order given and never re-sorts. Domain `ValueError` (e.g. blank summary)
  re-renders the page at 200 with the entered values preserved; `KeyError` → 404. HTMX requests get
  the `_timeline.html` fragment back, everything else gets a 303 redirect.
- **`templates/clients/_timeline.html`**: HTMX-swappable fragment. `<ol id="timeline">` of `<li>`
  entries, each with a `<time datetime=…>`, the kind, and the summary. Empty state renders a
  standalone `<p>No interactions yet</p>` with **no `<ol>` at all**.
- **`templates/clients/detail.html`**: extends base, single `<h1>`, `<dl>` of client fields,
  `role="alert"` error region rendered only on error, log-interaction form with every input
  label-bound (`for`/`id`), kind `<select>` driven from the domain `KINDS` tuple with the submitted
  value re-`selected`, then the included timeline and a back-link.

## Test coverage (`tests/web/test_interactions_ui.py`, 6 tests)
Detail page shows the client and orders the timeline newest-first (asserted by document position,
inserting out of order); empty state; kind `<select>` limited to the domain enum (and `"tweet"`
absent); whitespace-only summary re-renders accessibly at 200 and persists nothing; a valid log
persists and appears on the timeline; unknown client 404s.
**Full suite: 295 passed.**

## Build notes (local-LLM loop)
**Router by analogy — worked again, zero logic bounces.** Fed `pages_clients.py` as `--read` with
the contract as prose+signatures; qwen produced the router correctly on the first *applied* pass.
Verified empirically rather than by inspection: with the templates still stubbed, the POST path
already persisted correctly (the JSON API read-back returned the logged interaction) while the page
rendered empty — which isolated the remaining failures to the templates, not the router.

**One bounce, on the timeline fragment, for a defect the tests did not catch.** qwen nested the
empty-state `<p>` *inside* the `<ol>` — invalid HTML (only `<li>` may be an `<ol>` child), yet all
six tests passed, since they only assert the string "no interactions" appears. Caught by review,
not by red. The prompt had said "render this **instead of** the `<ol>`" in prose and that was
ignored; the bounce only worked once the exact `{% if %}`-wraps-`<ol>` structure was inlined as
code. The standing spoon-feed-as-code rule, now with a corollary: **tests passing is not evidence
the markup is valid** — accessibility/validity defects live in the gap the assertions don't cover.

**`detail.html` built first try**, including the label/`for` bindings and the `selected` round-trip.

**The first run of the router was lost to a new path-trap flavor — see lessons.md.** The stub's
docstring named `specs/task-crb32.md`; the model appended a second fence headed with that path,
`--yes-always` auto-accepted aider's "add it to the chat?", and the first round's edit was
discarded. Root cause reviewer-side again.
