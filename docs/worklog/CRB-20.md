# CRB-20 — Scaffold Next.js + TypeScript + tooling

**What was built**
A Next.js 15 (App Router) + TypeScript-strict project at the repo root, coexisting with the
Python code (removed later in CRB-38). Test runners, linting, formatting, and a health probe.

**Why**
Every later migration story (CRB-21…CRB-38) needs a working TS build + test harness. This story
is the foundation and is intentionally scaffolding, not test-first logic.

**Key decisions / trade-offs**
- **pnpm 9.15** via corepack; **Node 20** (`.nvmrc`). Installed userspace on code_vm (no Node/Docker/
  sudo there) via nvm.
- **ESLint** uses the classic `.eslintrc.json` (`next/core-web-vitals`) with
  `@typescript-eslint/no-unused-vars: error` — the conventions' "no unused imports" rule, enforced by
  `next lint`. Chose eslintrc over flat config for reliability with `eslint-config-next`.
- **Vitest** (jsdom, globals) for unit/component tests; **Playwright** for e2e (`e2e/`).
- `next-env.d.ts` is **committed** (not gitignored) so `pnpm typecheck` passes on a clean checkout
  without first running `next build`.
- `output: 'standalone'` in `next.config.mjs` for the future Nexlayer container build (CRB-19).
- `db:migrate` / `db:seed` scripts are present but inert until Prisma lands in CRB-21.

**Files**
`package.json`, `tsconfig.json`, `next.config.mjs`, `next-env.d.ts`, `.eslintrc.json`,
`.prettierrc.json`, `vitest.config.ts`, `vitest.setup.ts`, `playwright.config.ts`, `.env.example`,
`.nvmrc`, `src/app/{layout,page}.tsx`, `src/app/api/health/route.ts`, empty `src/{domain,server,lib}`
and `e2e/`, `tests/unit/{smoke,health}.test.ts`.

**Test coverage**
- `tests/unit/smoke.test.ts` — proves the Vitest runner works.
- `tests/unit/health.test.ts` — imports the health route handler and asserts `200 { status: "ok" }`.
- DoD gate: `pnpm install`, `pnpm typecheck`, `pnpm lint`, `pnpm test` all green.
