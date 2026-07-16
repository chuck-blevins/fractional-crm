# CRB-20 — Scaffold Next.js + TypeScript + tooling

**Linear:** [CRB-20](https://linear.app/crbc/issue/CRB-20/scaffold-nextjs-typescript-tooling)

**Phase 0 (foundation). Depends on: none. Note: scaffolding — reviewer/Claude may finish; not TDD-shaped.**

Stand up a Next.js 15 (App Router) + TypeScript project at the repo root, alongside the
existing Python code (which stays until CRB-38). This is the base every later story builds on.

## Deliverables
- `package.json` (pnpm) with scripts: `dev`, `build`, `start`, `lint`, `typecheck`
  (`tsc --noEmit`), `test` (vitest run), `test:watch`, `test:e2e` (playwright),
  `db:migrate`, `db:seed`.
- TypeScript **strict** (`tsconfig.json`: `strict`, `noUncheckedIndexedAccess`, `moduleResolution: bundler`).
- Next.js App Router under `src/app/`. `next.config.mjs`, `output: "standalone"` (needed for the container).
- ESLint (flat config, `no-unused-vars` = error) + Prettier.
- Vitest config (`vitest.config.ts`, `vitest.setup.ts`) with a `tests/unit/` root; Playwright config with an `e2e/` root.
- Directory skeleton: `src/app/`, `src/domain/`, `src/server/`, `src/lib/`, `tests/unit/`, `e2e/`.
- `.env.example` documenting `DATABASE_URL`, `NEXTAUTH_SECRET`, `NEXTAUTH_URL` (values added in later stories).
- Health route `src/app/api/health/route.ts` → `200 {"status":"ok"}`.

## Tests (authored as failing scaffold before implementation)
- `tests/unit/smoke.test.ts` — a trivial passing assertion (proves the runner works).
- `tests/unit/health.test.ts` — imports the `GET` handler from the health route and asserts
  it responds `200` with body `{ status: "ok" }`.

## Definition of Done
- `pnpm install`, `pnpm typecheck`, `pnpm lint`, `pnpm test` all succeed.
- Existing Python files untouched; `.gitignore` covers `node_modules/`, `.next/`, `coverage/`.
- Annotation + `docs/worklog/CRB-20.md` per conventions. Update `.agent/conventions.md` is
  already TS-oriented — do not revert it.
