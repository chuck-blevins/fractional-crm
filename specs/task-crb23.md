# CRB-23 — Reporting service

**Phase 1. Depends on: CRB-21, CRB-22.**

Port `reporting.py` (`active_engagements`, `monthly_run_rate`). Pure functions over a list of
engagements. Source of truth: `reporting.py`, `tests/test_reporting.py`.

## Deliverables (in `src/server/reporting.ts`)
- `activeEngagements(engagements)` — return only those with `status === "active"`,
  **input order preserved**.
- `monthlyRunRate(engagements)` — sum of `monthlyRate` over active engagements; `0` when none.
  Use a decimal-safe sum (avoid float drift; monthlyRate is `Decimal` from Prisma).
- A thin `getReportingSummary()` that reads engagements via `engagementService.list()` and
  returns `{ activeCount, monthlyRunRate }` for the dashboard (CRB-33).

## Tests
- `tests/unit/server/reporting.test.ts` — ported cases: filtering, order preservation, empty →
  `0`, mixed statuses, and a run-rate total matching the Python fixture.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-23.md` per conventions.
