# CRB-20 — Prisma schema + Postgres (core entities) + migrations + seed

**Phase 0. Depends on: CRB-19. Note: DB wiring — reviewer/Claude may finish.**

Model the CRM domain in Prisma against PostgreSQL. Enum values are fixed by
`.agent/conventions.md` and must match the Python code exactly.

## Deliverables
- `prisma/schema.prisma` with `provider = "postgresql"`, `DATABASE_URL` from env.
- Prisma enums: `ClientStatus`, `EngagementRole` (coo/cpo/advisor), `EngagementStatus`,
  `InteractionKind`, `MemberRole`, `IntegrationProvider`, `IntegrationStatus`.
- Models:
  - `Client`: `id` (cuid), `name`, `company`, `email @unique`, `status ClientStatus`,
    `engagementType EngagementRole`, `createdAt`, `updatedAt`. `email` is the natural key
    used elsewhere.
  - `Engagement`: `id`, `clientEmail` + relation to `Client.email`, `role EngagementRole`,
    `monthlyRate Decimal @db.Decimal(12,2)`, `startDate DateTime @db.Date`,
    `endDate DateTime? @db.Date`, `status EngagementStatus`, timestamps.
  - `Interaction`: `id`, `clientEmail` + relation, `date DateTime @db.Date`,
    `kind InteractionKind`, `summary`, `createdAt`. Index `(clientEmail, date desc)`.
  - `Team`: `id`, `name`. `TeamMember`: `id`, `teamId` + relation, `name`,
    `email`, `role MemberRole`. Unique `(teamId, email)`.
  - `Integration`: `id`, `provider IntegrationProvider @unique`, `externalId`,
    `status IntegrationStatus @default(connected)`, `lastSyncedAt DateTime?`.
- `prisma/seed.ts`: idempotent seed — one sample client + one active engagement.
- `src/lib/prisma.ts`: a singleton `PrismaClient` (avoid hot-reload connection storms).
- `docker-compose.yml` (dev/test Postgres 16 on 5432) so migrations and later repo tests can run.

## Tests
- `tests/unit/schema.test.ts` — import the generated enums and assert each contains exactly
  the allowed values from conventions (guards against typos/drift in enum values).

## Definition of Done
- `pnpm prisma validate` clean; `pnpm prisma migrate dev` applies to a fresh Postgres;
  `pnpm db:seed` runs twice without error (idempotent). `pnpm typecheck` clean.
- Annotation + `docs/worklog/CRB-20.md` per conventions.
