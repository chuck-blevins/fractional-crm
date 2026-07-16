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
