# Coding conventions (read on every task)

> The project is migrating from a Python CLI to a TypeScript web app.
> Phase 0+ stories (CRB-19 and up) are TypeScript. The Python source under
> `src/fractional_crm/` and `tests/` remains the **behavioral source of truth**
> until CRB-37 removes it — when a rule is unclear, the Python code and its
> tests decide it.

## Stack
- Next.js 15 (App Router), React 19, TypeScript in `strict` mode.
- PostgreSQL via Prisma. Input validation via Zod. Auth via NextAuth (Auth.js).
- Package manager: **pnpm**. Node 20+. ESM only.
- Tests: **Vitest** + React Testing Library (unit/component), **Playwright** (e2e).

## Rules
- Type everything. No `any` — use `unknown` + narrowing. `strict` stays on.
- Simplest correct implementation that passes the tests. Small, pure, well-named functions.
- NEVER edit, weaken, or delete anything under `tests/` or `e2e/`. Tests are the spec.
- Import ONLY what you use. No unused imports/vars (ESLint `no-unused-vars` is an error).
- Domain rules must stay identical to the ported Python behavior — same enum values,
  same status transitions, same error semantics (Python `ValueError` -> a thrown
  `ValidationError`; Python `KeyError` -> a thrown `NotFoundError`).
- Server/client boundary: mark client components `"use client"`; keep Prisma/DB access
  server-only (never import Prisma into a client component).
- Never commit secrets. Every env var is documented in `.env.example`.

## Per-task deliverables (EVERY story — enforced in review)
1. Make the story's tests pass; `pnpm lint` and `pnpm typecheck` are clean.
2. **Comprehensive annotation:** a TSDoc block (`/** ... */`) on every exported
   function, class, type, and Zod schema — purpose, `@param`, `@returns`, and
   `@throws`. Inline comments on any non-obvious branch (validation edges, state
   transitions, security-relevant code).
3. **Work summary:** create `docs/worklog/CRB-<n>.md` — what was built, why, key
   decisions/trade-offs, files touched, and how the tests cover it. One screen max.

## Enum reference (ported from Python — DO NOT change values)
- `Client.status`: prospect | active | paused | closed
- `Client.engagementType` / `Engagement.role`: coo | cpo | advisor
- `Engagement.status`: proposed | active | completed | cancelled
- `Interaction.kind`: call | email | meeting | note
- `TeamMember.role`: admin | member | guest
- `Integration.provider`: slack | github | gitlab | figma | intercom | zendesk
- `Integration.status`: connected | disconnected | error

## Client status transitions (state machine — identical to Python)
Allowed: `prospect->active`, `active->paused`, `paused->active`, `active->closed`,
`paused->closed`. Any other transition throws `ValidationError` and leaves status unchanged.

## Email validation (identical to Python — the model got this wrong repeatedly)
Reject: empty/whitespace local part (before `@`), empty domain (after `@`), any
whitespace anywhere, a domain without a dot, and a TLD shorter than 2 chars.
Use a regex — a naive "has `@` and `.`" check is insufficient.
