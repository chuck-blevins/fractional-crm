# Migration epic: Python CLI → TypeScript web app (CRB-19 … CRB-37)

Goal: replace the Python/SQLite CLI with a Next.js (App Router, TS) + Prisma + Postgres
web app, preserving 100% of the domain behavior locked in by the existing Python tests,
then remove the Python code. Target deploy: single `app` pod + `db` postgres pod on
Nexlayer (topology already scaffolded on the `nexlayer` branch).

Each story = one `specs/task-crbN.md` + one `crb-N-*` branch + one PR to `main`, built
test-first. Definition-of-Done for every story includes comprehensive TSDoc annotation
and a `docs/worklog/CRB-N.md` work summary (see `.agent/conventions.md`).

## Sequence & dependencies

| # | Story | Depends on |
|---|-------|-----------|
| CRB-19 | Scaffold Next.js + TS + tooling (Vitest/Playwright/ESLint) + TS conventions | — |
| CRB-20 | Prisma schema + Postgres (core entities, enums) + migrations + seed | 19 |
| CRB-21 | Domain layer in TS (Zod validators + status state-machine) | 19 |
| CRB-22 | Repository/service layer over Prisma (clients, engagements) | 20, 21 |
| CRB-23 | Reporting service (active engagements, monthly run-rate) | 21, 22 |
| CRB-24 | CSV import/export + JSON importer + formula-injection hardening | 21, 22 |
| CRB-25 | API: Clients CRUD + status transitions | 22 |
| CRB-26 | API: Engagements CRUD | 22 |
| CRB-27 | API: Interactions (log + list newest-first) | 22 |
| CRB-28 | API: Teams + Integrations | 22 |
| CRB-29 | API: CSV import/export endpoints | 24, 25 |
| CRB-30 | Auth: NextAuth Google OAuth + session-gated routes | 19, 20 |
| CRB-31 | UI: app shell, nav, auth-gated dashboard | 30 |
| CRB-32 | UI: Clients (list/create/edit/status) | 25, 31 |
| CRB-33 | UI: Engagements + run-rate/reporting widgets | 26, 23, 31 |
| CRB-34 | UI: Interactions timeline per client | 27, 31 |
| CRB-35 | UI: Teams + Integrations | 28, 31 |
| CRB-36 | UI: CSV import/export | 29, 31 |
| CRB-37 | Remove Python app; rewrite README/USAGE for the web app | all |

## Reviewer notes (local qwen2.5-coder-7b limits)
Foundation stories 19, 20, and 30 (scaffolding, Prisma wiring, OAuth) are poorly suited
to the local 7B and will likely be finished by Claude/reviewer. Domain and API stories
(21–29) are the sweet spot: pure functions + explicit contracts + failing tests. UI
stories (31–36) need a scaffolded component test per story to keep the model on-rails.
