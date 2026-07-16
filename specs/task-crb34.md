# CRB-34 — UI: Engagements + run-rate / reporting widgets

**Linear:** [CRB-34](https://linear.app/crbc/issue/CRB-34/ui-engagements-run-rate-reporting-widgets)

**Phase 4. Depends on: CRB-27, CRB-24, CRB-32.**

## Deliverables
- `src/app/(dashboard)/engagements/page.tsx`: list (filterable by client), create/edit forms
  posting to the Engagements API. Enforce `monthlyRate > 0` and `endDate >= startDate` in the form.
- Dashboard widgets (fill the CRB-32 slots): **Active engagements** count and **Monthly run-rate**
  from `getReportingSummary()` / a `/api/reporting/summary` route. Format currency; run-rate `$0`
  when none active.
- A small chart is optional; correctness of the numbers is the requirement.

## Tests
- `tests/unit/ui/engagements.test.tsx` — form rejects `monthlyRate <= 0` and `endDate < startDate`
  inline; widgets render the run-rate from a mocked summary.
- `e2e/engagements.spec.ts` — add an active engagement; the run-rate widget increases accordingly.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-34.md` per conventions.
