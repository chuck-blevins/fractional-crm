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
