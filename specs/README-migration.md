# Migration epic: Python CLI → TypeScript web app (CRB-20 … CRB-38)

Goal: replace the Python/SQLite CLI with a Next.js (App Router, TS) + Prisma + Postgres
web app, preserving 100% of the domain behavior locked in by the existing Python tests,
then remove the Python code. Target deploy: single `app` pod + `db` postgres pod on
Nexlayer (topology already scaffolded on the `nexlayer` branch; deploy work tracked
separately as CRB-19 "Deploy via NexLayer").

Each story = one `specs/task-crbN.md` + one `crb-N-*` branch + one PR to `main`, built
test-first. Definition-of-Done for every story includes comprehensive TSDoc annotation
and a `docs/worklog/CRB-N.md` work summary (see `.agent/conventions.md`).

## Sequence & dependencies

| # | Story | Depends on |
|---|-------|-----------|
| CRB-20 | Scaffold Next.js + TS + tooling (Vitest/Playwright/ESLint) + TS conventions | — |
| CRB-21 | Prisma schema + Postgres (core entities, enums) + migrations + seed | CRB-20 |
| CRB-22 | Domain layer in TS (Zod validators + status state-machine) | CRB-20 |
| CRB-23 | Repository/service layer over Prisma (clients, engagements) | CRB-21, CRB-22 |
| CRB-24 | Reporting service (active engagements, monthly run-rate) | CRB-22, CRB-23 |
| CRB-25 | CSV import/export + JSON importer + formula-injection hardening | CRB-22, CRB-23 |
| CRB-26 | API: Clients CRUD + status transitions | CRB-23 |
| CRB-27 | API: Engagements CRUD | CRB-23 |
| CRB-28 | API: Interactions (log + list newest-first) | CRB-23 |
| CRB-29 | API: Teams + Integrations | CRB-23 |
| CRB-30 | API: CSV import/export endpoints | CRB-25, CRB-26 |
| CRB-31 | Auth: NextAuth Google OAuth + session-gated routes | CRB-20, CRB-21 |
| CRB-32 | UI: app shell, nav, auth-gated dashboard | CRB-31 |
| CRB-33 | UI: Clients (list/create/edit/status) | CRB-26, CRB-32 |
| CRB-34 | UI: Engagements + run-rate/reporting widgets | CRB-27, CRB-24, CRB-32 |
| CRB-35 | UI: Interactions timeline per client | CRB-28, CRB-32 |
| CRB-36 | UI: Teams + Integrations | CRB-29, CRB-32 |
| CRB-37 | UI: CSV import/export | CRB-30, CRB-32 |
| CRB-38 | Remove Python app; rewrite README/USAGE for the web app | all |

## Reviewer notes (local qwen2.5-coder-7b limits)
Foundation stories CRB-20, CRB-21, and CRB-31 (scaffolding, Prisma wiring, OAuth) are poorly
suited to the local 7B and will likely be finished by Claude/reviewer. Domain and API stories
(CRB-22…CRB-30) are the sweet spot: pure functions + explicit contracts + failing tests. UI
stories (CRB-32…CRB-37) need a scaffolded component test per story to keep the model on-rails.
