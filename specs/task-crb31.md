# CRB-31 — Auth: NextAuth (Auth.js) Google OAuth + session-gated routes

**Linear:** [CRB-31](https://linear.app/crbc/issue/CRB-31/auth-nextauth-authjs-google-oauth-session-gated-routes)

**Phase 3. Depends on: CRB-20, CRB-21. Note: OAuth wiring — reviewer/Claude likely finishes.**

Add authentication for the **app user** (the fractional COO/CPO operating the CRM) via NextAuth
with Google OAuth. This replaces the Python per-client auth modules (`passcode.py`,
`verification.py`, `sso.py`) at the app boundary. Those per-client mechanisms are NOT ported to
the UI in this migration — capture that decision in the worklog (they can return later as a
"client portal" epic if wanted).

## Deliverables
- NextAuth v5 (Auth.js) config `src/lib/auth.ts` with the Google provider; Prisma adapter
  (add the Auth.js models — `User`, `Account`, `Session`, `VerificationToken` — to
  `prisma/schema.prisma` + a migration).
- `src/app/api/auth/[...nextauth]/route.ts` handler.
- `middleware.ts`: gate everything except `/`, `/api/health`, `/api/auth/**`, and static assets.
  Unauthenticated API calls → `401`; unauthenticated page loads → redirect to sign-in.
- `.env.example`: add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `NEXTAUTH_SECRET`, `NEXTAUTH_URL`.
- `auth()` helper usable in server components and route handlers to read the session.

## Tests
- `tests/unit/auth/middleware.test.ts` — a request without a session to a protected API route
  gets `401`; `/api/health` stays public.
- `e2e/auth.spec.ts` (Playwright) — visiting a protected page while signed out redirects to
  sign-in. (Mock/stub the provider; do not hit Google in CI.)

## Definition of Done
- `pnpm test` green; `pnpm typecheck` + `pnpm lint` clean; migration applies.
- No secrets committed. Annotation + `docs/worklog/CRB-31.md` per conventions (include the
  "per-client auth intentionally deferred" decision).
