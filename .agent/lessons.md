# Lessons (appended by reviewer over time)

## proof/task-001 (fizzbuzz) — 2026-07-10
- Model added an unused `from typing import List`. RULE: no unused imports; import only what is used.

## CRB-8 (Client model) — 2026-07-10 (reviewer bounce)
- Email validation must reject: empty local part (before @), empty domain (after @), any whitespace, and a domain without a dot+2char TLD. Naive "@ and . present" is insufficient.
- REPEAT OFFENSE: unused `from typing import List` added again. Remove ALL unused imports before finishing.

## CRB-8 outcome — 2026-07-10
- Model reached 8/9 twice; could not reject empty domain label (a@.co). Reviewer finished with a regex validator.
- TAKEAWAY: for fiddly input-validation edges (regex-class), give the model the exact rule set OR expect reviewer to finish. Don't merge on "mostly passing".
