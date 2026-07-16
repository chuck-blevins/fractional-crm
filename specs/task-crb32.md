# CRB-32 — UI: app shell, nav, auth-gated dashboard

**Linear:** [CRB-32](https://linear.app/crbc/issue/CRB-32/ui-app-shell-nav-auth-gated-dashboard)

**Phase 4. Depends on: CRB-31.**

The application frame every feature page renders inside.

## Deliverables
- `src/app/layout.tsx`: root layout, global styles, session provider.
- A sidebar/topbar nav linking Clients, Engagements, Interactions, Teams, Integrations, Import/Export.
- Signed-out state shows a "Sign in with Google" screen; signed-in shows the shell + the user's name/avatar + sign-out.
- `src/app/(dashboard)/page.tsx`: dashboard placeholder with slots for the reporting widgets (filled in CRB-34).
- Reusable primitives in `src/components/` (Button, Card, Table, form Field) — keep minimal and typed.

## Tests
- `tests/unit/ui/nav.test.tsx` (RTL) — nav renders all six links; sign-out control present when a
  session is provided (mock the session).
- `e2e/dashboard.spec.ts` — signed-in user lands on the dashboard and sees the nav.

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean.
- Annotation + `docs/worklog/CRB-32.md` per conventions.
