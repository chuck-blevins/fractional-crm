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
