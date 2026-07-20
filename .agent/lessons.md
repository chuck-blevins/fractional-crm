# Lessons (appended by reviewer over time)

## proof/task-001 (fizzbuzz) — 2026-07-10
- Model added an unused `from typing import List`. RULE: no unused imports; import only what is used.

## CRB-8 (Client model) — 2026-07-10 (reviewer bounce)
- Email validation must reject: empty local part (before @), empty domain (after @), any whitespace, and a domain without a dot+2char TLD. Naive "@ and . present" is insufficient.
- REPEAT OFFENSE: unused `from typing import List` added again. Remove ALL unused imports before finishing.

## CRB-8 outcome — 2026-07-10
- Model reached 8/9 twice; could not reject empty domain label (a@.co). Reviewer finished with a regex validator.
- TAKEAWAY: for fiddly input-validation edges (regex-class), give the model the exact rule set OR expect reviewer to finish. Don't merge on "mostly passing".

## CRB-10 (Engagement) — 2026-07-11 (reviewer bounce)
- When a field is specified as an ISO date STRING and tests assert equality with that string, STORE the original string. Validate by parsing (datetime.date.fromisoformat) to check validity, but keep and store the caller's string value — do not store the parsed date object.
- Never stub a validator. _validate_client_email must actually reject invalid emails (no '@', empty local part, no dotted domain), not just .strip(). Use a regex.

## CRB-10 outcome — 2026-07-11
- Two bounces couldn't get "store the ISO string, still validate ordering" right (model created duplicate _str attrs and dropped the end>=start check). Reviewer finished.
- TAKEAWAY: when a task needs a field validated one way but stored another (parse-to-check, store-original), spell out BOTH explicitly and keep all prior constraints in the retry message, or expect to finish it.

## CRB-12 (SQLite persistence) — 2026-07-11 (reviewer fix)
- REPEAT OFFENSE (3rd time): model imported `from typing import Dict, List` but used only List. Reviewer removed the unused `Dict`. Import ONLY names actually referenced.

## CRB-2 (Team/TeamMember) — 2026-07-11 (reviewer cleanup)
- Model reached green but pulled in `from collections import OrderedDict` where a plain dict suffices (Python 3.12 preserves insertion order, matching repository.py). Prefer the existing plain-dict idiom; do not add OrderedDict for ordering alone.

## CRB-4 (client data importer) — 2026-07-11 (reviewer cleanup)
- REPEAT OFFENSE (4th time): model wrote `from typing import List, Dict` but never referenced `Dict`. Reviewer removed it. Import ONLY names actually used — `csv.DictReader` is not a `typing.Dict` reference.

## CRB-20 (FastAPI scaffold) — 2026-07-16
- With `--auto-test` ON for a GREENFIELD file-creation task, qwen2.5-coder-7b saw the red pytest
  output, latched onto "environment problem", and emitted conversational venv/pytest advice instead
  of file listings — never conforming to aider's whole-edit format ("No filename provided before ```").
- FIX (loop rule): for creating NEW files, run aider WITHOUT `--auto-test` — generate first, run the
  test yourself after. Keep the message tiny and format-forward (say "output ONLY each file as a
  fenced block preceded by its path; do not run shell commands or give environment advice"). Pass the
  target TEST file as `--read` so the contract is unambiguous; drop the long spec/conventions for
  micro-tasks (extra tokens distract the 7B).

## CRB-21 (config/deps wiring) — 2026-07-16
- Green on the FIRST try WITHOUT `--auto-test` — confirms the CRB-20 fix (no auto-test on greenfield).
- BUT the model copied a literal `# one-line docstring` placeholder from the prompt into the code as a
  comment instead of writing a real docstring (convention violation caught at the review gate).
- LESSON (prompting): never put placeholder tokens like `# one-line docstring` in the contract — the
  7B reproduces prompt text verbatim. Give the ACTUAL docstring text you want, or say "each function
  begins with a triple-quoted one-line docstring describing its return value."

## CRB-22 (Clients API) — 2026-07-16
- First MULTI-FILE story (errors.py + routers/__init__.py + clients.py + app.py EDIT). qwen2.5-coder-7b
  produced nothing usable in one shot: new files stayed empty and app.py was not edited. The
  pseudocode-style contract (`@router.get("") -> list of ClientOut:`) is not valid Python and confused it.
- LESSON: for the 7B on router/multi-file stories — (1) give VALID Python as the contract, not
  pseudocode; (2) keep each aider run to as few files as possible; (3) editing an existing file
  (e.g. app.py include_router) is unreliable when bundled with new-file creation — the reviewer should
  own small wiring edits, or run them separately. Providing near-complete valid code is the realistic
  "tight spec" at this model size for API routers.
- OUTCOME: even with exact valid Python provided, two aider passes emitted no files (whole-format not
  applied). Reviewer authored the 4 files directly (last resort). RECOMMENDATION for router stories:
  split into separate aider runs — (a) errors.py, (b) the single router file, (c) app.py include_router
  as its own edit — or accept reviewer authorship for routers until a stronger local model is used
  (qwen3.6-35b is available on .12 but slow/thinking). Single-file tool/function stories remain fine.

## AIDER MULTI-FILE FAILURE — diagnosed 2026-07-16 (from CRB-22 chat history)
- ROOT CAUSE: qwen2.5-coder-7b returns an EMPTY/failed response when asked to emit ~4 files in ONE
  aider run (CRB-22 run b: no assistant reply recorded, 0 edits applied). Pseudocode contracts (run a)
  make it ramble off-task. Runs that SUCCEEDED (CRB-20, CRB-21) emitted 1-2 SMALL files from a concise
  DESCRIPTIVE contract.
- CONCLUSION: the ceiling is OUTPUT SIZE / FILE COUNT per run, not capability.
- PROTOCOL for router / multi-file stories (use this going forward):
  1. ONE file per aider run (never bundle new files + edits).
  2. Concise DESCRIPTIVE contract with valid signatures — NOT pseudocode, NOT a full-code paste
     (pasting the whole solution made the model return empty).
  3. Wire the router into app.py as its OWN separate one-line-edit run.
  4. Reviewer authors only if a single-file run still fails after a tighter bounce.

## CORRECTION (2026-07-16) — the CRB-22/23 failures were the MODEL ENDPOINT, not prompt size
- The "AIDER MULTI-FILE FAILURE / output-size ceiling" protocol above was a PREMATURE diagnosis.
- Real cause: the LM Studio endpoint on .12 went unresponsive around CRB-22 (~14:50). A DIRECT trivial
  chat completion (`say hi`, 20 tokens) times out — the server answers /v1/models (metadata) but hangs
  on /v1/chat/completions. CRB-20/21 worked earlier because the box was healthy then.
- DIAGNOSTIC RULE: when aider produces empty output (no "Tokens received" line), FIRST curl
  /v1/chat/completions directly with a trivial prompt before blaming the prompt/aider. Distinguish a
  dead/slow model box from a genuine model-capability limit.
- The single-file-per-run / descriptive-contract guidance is still reasonable practice, but it was NOT
  what caused these failures. Re-test the 7B's true router ceiling only once the .12 box is healthy.

## CRB-23 (Engagements API) — 2026-07-16 (healthy box)
- With the .12 box healthy, qwen2.5-coder-7b BUILT the single-file router via aider (75 lines, applied)
  AND wired app.py via a separate single-file edit run — confirming the one-file-per-run protocol works
  and the earlier failures were purely the wedged endpoint.
- Review gate caught: (1) model omitted docstrings again (state the docstring requirement per-function);
  (2) it filtered the list via repo.get() (500s on a missing key) instead of a list comprehension;
  (3) it wrote `async def` endpoints — the sync sqlite repo is THREAD-BOUND, so an async handler uses the
  connection from a different thread than the dependency → sqlite3.ProgrammingError "created in a thread".
- RULE: endpoints that touch the sqlite repos must be plain `def` (sync), matching clients.py — keeps the
  Depends() dependency and the handler in the same threadpool thread. (Alt: check_same_thread=False, but
  sync def is simpler and already the house style.)
- FOLLOW-UP: when asked to change `async def`->`def`, the 7B rewrote the functions but DROPPED all the
  `@router.*` decorators, so no routes registered (blanket 404s). RULE: on any "edit the endpoints"
  bounce, restate the EXACT decorator that must sit above each function — the model loses them when
  rewriting function signatures.

## CRB-25 (Teams + Integrations) — 2026-07-16
- qwen emitted the filename header WITHOUT the directory prefix ("sqlite_integration_repository.py"
  instead of "src/fractional_crm/sqlite_integration_repository.py"), so aider wrote the file to the
  REPO ROOT and left the intended path as a 0-byte file.
- TRAP: `ast.parse("")` succeeds — an empty file "parses". Do NOT use ast-parse to confirm a build;
  check `wc -l` on the INTENDED path (non-zero) instead.
- RULE: after each aider run, verify the file exists AND is non-empty at the intended path; if aider
  reports "Applied edit to <name>" without the expected directory, the model dropped the prefix —
  relocate the file (reviewer mechanical fix) or restate the full path prominently and re-run.

## CRB-28 (passcode login + gating) — 2026-07-16
- The one-file wiring run hit the CRB-25 path-prefix trap AGAIN: the 7B emitted the fenced
  header as bare "app.py" (no src/fractional_crm/web/ prefix), so aider created a NEW file at
  the REPO ROOT and left the real app.py untouched (exit 0, "Applied edit to app.py"). The
  CONTENT was correct — only the path was wrong. RULE: when the target is a nested path, state
  in the prompt "the fenced code block header MUST be the full path src/fractional_crm/web/app.py",
  and after every run assert the intended path changed (git diff --name-only) AND no stray file
  appeared at the repo root (git status --porcelain for new top-level *.py).
- Docstrings omitted again on ~half the functions/routes despite the standing rule. For any file
  with N public functions, the prompt should enumerate each signature WITH its one-line docstring
  text, not just say "docstrings on all". Reviewer added them this time.

## CRB-29 (base layout + nav) — 2026-07-16
- POSITIVE: pre-creating each target file as a STUB (so aider does an in-place EDIT, not a
  CREATE) sidestepped the path-prefix trap entirely — base.html and style.css both landed at
  the correct nested path, zero stray root files, zero bounces. Adopt for all nested-file
  stories: reviewer stubs the file first, then aider edits it.
- With an exact accessible-markup spec, the 7B reproduced base.html (skip link, semantic
  landmarks, aria-current conditionals, HTMX tag) correctly first try. HTML/CSS to a tight
  spec is within the 7B reach.
- REVIEW CATCH: the model wrapped the header brand in <h1>, which plus the page <h1> gives two
  h1s (WCAG "one h1 per page"). RULE: in layout specs, state the brand/site-name is a plain
  link and the SINGLE <h1> comes from the page content block.
- OPS: never append lessons via an inline `<< "EOF"` heredoc inside a single-quoted ssh
  command — a stray EOF-match failure leaks the rest of the script into the file. scp a file
  and `cat file >> .agent/lessons.md` instead. Also rm .agent/prompt-*.txt before committing.

## CRB-30 (Clients UI) — 2026-07-16
- The stub-first / in-place-edit approach held up on a 3rd story: both templates built by the 7B
  with ZERO bounces and ZERO stray files. This is now the default for every nested-file build.
- TRAP (reviewer-side, FastAPI): a POST handler annotated `-> HTMLResponse | RedirectResponse`
  makes FastAPI try to build a response model from the union and raises at import
  ("Invalid args for response field"). Annotate multi-return handlers as `-> Response` (or set
  `response_model=None` on the decorator). GET handlers returning a single Response subclass are fine.
- To let the UI honour the domain's rules without duplicating them, expose the domain's data as
  module constants (ALLOWED_TRANSITIONS, STATUSES, ENGAGEMENT_TYPES) via a pure refactor and pass
  them into the template context — do NOT re-encode the state machine in the web layer.

## OPS — merging a STACKED PR chain (learned the hard way, 2026-07-17)
- NEVER `gh pr merge N --merge --delete-branch` on a PR that another PR is stacked on.
  Deleting the base branch does NOT retarget the dependent PR — GitHub silently **auto-CLOSES**
  it (state=CLOSED, mergeable=CONFLICTING). You then hit a deadlock: you cannot reopen it (its
  base branch no longer exists) and you cannot retarget it ("Cannot change the base branch of a
  closed pull request").
- The `--delete-branch` habit from CRB-22..27 is safe ONLY because those were independent
  branches cut from main. A stack (#28 <- #29 <- #30) is a different animal.
- CORRECT procedure for a stack, bottom-up:
    1. `gh pr merge <bottom> --merge`        # NO --delete-branch
    2. `gh pr edit <next> --base main`       # retarget explicitly; don't trust auto-retarget
    3. repeat up the stack
    4. only at the very END, delete the branches — and verify first:
       `git merge-base --is-ancestor origin/<branch> origin/main`
- RECOVERY if you already did it: the merge commit's second parent IS the deleted branch tip.
    `git push origin <merge_sha>^2:refs/heads/<branch>`   # restore
    `gh pr reopen N` && `gh pr edit N --base main`        # then merge normally
- Corollary: `gh pr merge` prints NOTHING on success. Don't read silence as failure — verify with
  `gh pr view N --json state,mergedAt` and check `git log --first-parent origin/main`.

## CRB-39 (login rate limit) — 2026-07-17
- PATH-PREFIX TRAP RECURS ON BOUNCES, even when the target was pre-stubbed. The pre-stub only
  guarantees the FIRST run is an edit-not-create; on run 2 the 7B emitted the fence header as the
  bare basename again and aider wrote a stray `./ratelimit.py` at the repo root while the real
  target kept the old (buggy) content — so the tests failed *identically* to the previous run,
  which looks exactly like "the model ignored the bounce". It hadn't; the content was correct, at
  the wrong path.
  RELIABLE TELL: read aider's own closing line. `Applied edit to src/fractional_crm/web/foo.py`
  = fine. `Applied edit to foo.py` (bare basename) = the trap fired. Diff the two runs' log lines.
  Also: aider STAGES the stray (`AM` in git status), so a careless `git add .` / `git commit -a`
  would commit it. Check `git status --porcelain` after EVERY aider run, not just the first, and
  `find . -maxdepth 1 -name "*.py"` before committing.
  RECOVERY: if the stray's content is correct, `git restore --staged <stray>` + `mv` it onto the
  intended path. That is a PATH fix, not a reviewer-authored implementation — the model still
  wrote the code, so it does not count as a ghostwrite.
- The 7B ignored two EXPLICIT prose spec bullets on run 1: it locked on the first failure (never
  compared the count to `max_failures`) and used a bare `int(os.getenv(...))` that raises on a
  typo'd env value. Prose rules about a CONDITIONAL ("only lock once count reaches N") and about
  DEFENSIVE parsing ("must never raise") do not reliably survive; the bounce only worked once the
  exact `if/else` and `try/except` blocks were inlined verbatim in the prompt. Confirms the standing
  ceiling: good drafter, not a finisher — spoon-feed edge/conditional logic as code, not prose.
- SECURITY RULE for any auth throttle: the lockout check must run BEFORE the password hash. PBKDF2
  is ~134ms of CPU per call, so hashing a locked-out attempt turns the lockout into a DoS amplifier
  instead of a defence. Pin it with a test that spies on the verify function and asserts it is never
  called while locked — behaviour, not inspection.
- Corollary: do NOT "harden" by raising PBKDF2 iterations while an endpoint is unthrottled. It
  makes the unauthenticated CPU burn worse. Rate limit first, iterations second.

## CRB-31 (engagements UI + dashboard) — 2026-07-17
- ROUTER-BY-ANALOGY WORKS. Given an existing router (pages_clients.py) as `--read` plus the deltas
  as prose, the 7B reproduced the whole pattern for a new model (engagements) correctly bar one bug.
  This extends the proven envelope beyond templates: the local loop can ADAPT an existing pattern,
  not only fill markup. Do it this way for CRB-32/33 (interactions, teams+integrations) — feed the
  nearest existing pages_*.py as the reference.
- THE ONE BUG was the usual last-10%: it added a new filter param to the leaf helper (_rows) and to
  the caller (the handler) but not to the MIDDLE helper (_list_response) they pass through, so the
  keyword arg hit a function that didn't accept it -> TypeError on every list request. When you add
  a param that flows caller->helper->leaf, the bounce prompt must name EVERY function in the chain.
- NEW PATH-TRAP FLAVOR — "wrong-file fence via repo-map contamination". A fragment stub that begins
  `{% extends "base.html" %}` makes aider pull base.html into its repo-map; the 7B then labels its
  (correct) output block with `base.html` instead of the target. Result: a SILENT no-op — NO stray
  file at repo root, NO "Applied edit" line, just aider printing "please add base.html to the chat".
  The content was right all along; only the fence path was wrong. Diagnostic tell: build "succeeded"
  but the target file is byte-for-byte the stub AND the log ends with an "add <file> to the chat"
  request. FIX: fragment/partial stubs must NOT extend base.html and should be a bare one-line
  comment — keep sibling templates out of aider's context so the model has no wrong name to grab.
- Reminder reinforced: after EVERY aider run confirm the target actually changed
  (`wc -l` / `git diff --stat <path>`), not just that aider exited. "No stray at root" is necessary
  but NOT sufficient — this trap mis-targets an existing sibling, not the root.

## CRB-32 (client detail + interactions timeline) — 2026-07-18
- ROUTER-BY-ANALOGY CONFIRMED A SECOND TIME. Same recipe as CRB-31 (nearest existing `pages_*.py`
  as `--read`, deltas as prose + exact signatures) produced a correct router on the first applied
  pass, this time with no logic bounce at all. Treat this as the default method for CRB-33/34.
- NEW PATH-TRAP FLAVOR (3rd) — "wrong-file fence via a path named in the STUB ITSELF". The router
  stub's DOCSTRING read "STUB — not yet implemented. Specified by specs/task-crb32.md and pinned by
  tests/web/test_interactions_ui.py." The 7B emitted the correct router, then a SECOND fence headed
  `specs/task-crb32.md` containing filler prose. `--yes-always` auto-answered aider's "add
  specs/task-crb32.md to the chat?" prompt, which started a whole second LLM round (11k sent, 35
  received) and the FIRST round's edit was silently DISCARDED. Tells: no "Applied edit" line,
  `git diff --stat` empty, and a second file-path header near the end of the log.
  This GENERALISES the CRB-31 `{% extends %}` finding: it is not about Jinja inheritance, it is
  about **any filename visible to the model**. RULE: a pre-stub must reference NO other file path
  in any form — not an extends, not a docstring, not a comment. Keep stubs to a bare one-liner.
  Belt-and-braces: pass `--map-tokens 0` on single-file runs so the repo-map contributes no
  filenames either. Re-running the IDENTICAL prompt against a minimised stub applied cleanly.
- TESTS PASSING != MARKUP CORRECT. The timeline fragment put the empty-state `<p>` inside the
  `<ol>` — invalid HTML — and all 6 tests passed anyway, because they only assert that the string
  "no interactions" is present. The reviewer caught it by reading the output, not by running red.
  On accessibility-scoped stories, READ the generated markup; the assertions pin behaviour, not
  validity. (Fixing it needed the exact `{% if %}`-wraps-`<ol>` structure inlined as code — prose
  saying "instead of the `<ol>`" was ignored. Spoon-feed-as-code rule, again.)
- USEFUL DIAGNOSTIC PATTERN: when a UI story fails, check whether the ROUTER is already correct by
  probing the JSON API for the same data. Here the POST path persisted correctly (API read-back
  returned the interaction) while the page rendered empty — which proved the router was done and
  isolated all 5 remaining failures to the still-stubbed templates in one step.
