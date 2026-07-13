# Nexlayer — fractional-crm

<!-- nexlayer:meta version=1 analyzed=2026-07-13T17:07:23Z repo=https://github.com/chuck-blevins/fractional-crm branch=main -->

> **For AI agents (Claude Code, Cursor, Gemini CLI, Copilot):**
> This file is the **project context** for this Nexlayer deployment — tech stack, env vars, secrets, live URL.
> For full platform detail (nexlayer.yaml schema, Dockerfile rules, CI/CD, task recipes) read **`nexlayer.skills`** in this repo.
>
> **Critical rules (full detail in `nexlayer.skills`):**
> - Inter-pod refs: `${podName:port}` only — never `localhost` or bare hostnames
> - Docker Hub images: prefix with `mirror.gcr.io/library/` — bare tags fail on the cluster
> - Secrets: set in the Nexlayer dashboard — never commit to `nexlayer.yaml` or Dockerfile
>
> **This file:** `agent-managed` sections update automatically. `user-editable` sections (Local Development Setup, Nexlayer Deployment Plan, Build Notes) are yours — preserved across re-analysis.

## Project Summary
<!-- nexlayer:section agent-managed=project_summary -->
A CRM system designed specifically for Fractional COO/CPO professionals to manage clients and operations.
<!-- nexlayer:end -->

## Technology Stack
<!-- nexlayer:section agent-managed=tech_stack -->
| Name | Kind | Version | Detected From |
|------|------|---------|---------------|
| Next.js | framework | unknown | README.md |
| PostgreSQL | database | 16 | README.md |
| Node.js | language | 20 | README.md |
<!-- nexlayer:end -->

## Repository Structure
<!-- nexlayer:section agent-managed=structure_map -->
- README.md — Project entry point and overview
<!-- nexlayer:end -->

## External Services Required
<!-- nexlayer:section agent-managed=external_deps -->
_No external services detected._
<!-- nexlayer:end -->

## Local Development Setup
<!-- nexlayer:section user-editable=local_setup -->
### Prerequisites

- Node.js >= 20
- pnpm

### Environment variables

Copy `.env.example` to `.env.local` and fill in:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/fractional_crm
```

### Steps

1. `pnpm install` — Install project dependencies
2. `pnpm dev` — Start the Next.js development server

<!-- nexlayer:end -->

## Nexlayer Setup
<!-- nexlayer:section agent-managed=nexlayer_setup -->
### Pod Environment Variables

| Pod | Variable | Value | Kind |
|-----|----------|-------|------|
| `app` | `NODE_ENV` | `production` | plain |
| `app` | `PORT` | `"3000"` | plain |
| `app` | `DATABASE_URL` | `"postgresql://app:${POSTGRES_PASSWORD}@db.pod:5432/app"` | inter-pod |
| `app` | `NEXTAUTH_SECRET` | `${NEXTAUTH_SECRET}` | inter-pod |
| `db` | `POSTGRES_USER` | `"app"` | plain |
| `db` | `POSTGRES_PASSWORD` | `${POSTGRES_PASSWORD}` | inter-pod |
| `db` | `POSTGRES_DB` | `"app"` | plain |
| `fractional-crm-postgres-data` | `size` | `10Gi` | plain |
| `fractional-crm-postgres-data` | `mountPath` | `/var/lib/postgresql` | plain |

### nexlayer.yaml

```yaml
application:
  name: fractional-crm
  pods:
    - name: app
      image: "registry.nexlayer.io/user_01krc13rb1z2ng6b0bdm6h6wab/fractional-crm:19f5c725c97"
      path: /
      servicePorts:
        - 3000
      vars:
        NODE_ENV: production
        PORT: "3000"
        DATABASE_URL: "postgresql://app:${POSTGRES_PASSWORD}@db.pod:5432/app"
        NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
    - name: db
      image: mirror.gcr.io/library/postgres:16-alpine
      servicePorts:
        - 5432
      vars:
        POSTGRES_USER: "app"
        POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
        POSTGRES_DB: "app"
      volumes:
        - name: fractional-crm-postgres-data
          size: 10Gi
          mountPath: /var/lib/postgresql
```

<!-- nexlayer:end -->

## Nexlayer Deployment Plan
<!-- nexlayer:section user-editable=deployment_plan -->
### Pod Topology

| Pod | Image | Port | Role |
|-----|-------|------|------|
| crm-web | mirror.gcr.io/library/node:22-alpine | 3000 | web |
| crm-db | mirror.gcr.io/library/postgres:16-alpine | 5432 | database |

### Deployment notes

- The application pod connects to the database using the Nexlayer mandated address: crm-db.pod:5432
- Mirror GCR is used for all official library images to comply with platform rules

<!-- nexlayer:end -->

## Build Notes
<!-- nexlayer:section user-editable=build_notes -->
<!-- Add notes for future builds here — preserved across re-analysis -->
<!-- nexlayer:end -->

## Nexlayer Configuration
<!-- nexlayer:section agent-managed=nexlayer_config -->
**Last deployed:** 2026-07-13T17:10:16Z  
**Live URL:** https://flamboyant-goshawk-fractional-crm.cloud.nexlayer.ai  
**Runtime:** docs · **Port:** 3000  
**Deploy branch:** main  

```yaml
application:
  name: fractional-crm
  pods:
    - name: app
      image: "registry.nexlayer.io/user_01krc13rb1z2ng6b0bdm6h6wab/fractional-crm:19f5c725c97"
      path: /
      servicePorts:
        - 3000
      vars:
        NODE_ENV: production
        PORT: "3000"
        DATABASE_URL: "postgresql://app:${POSTGRES_PASSWORD}@db.pod:5432/app"
        NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
    - name: db
      image: mirror.gcr.io/library/postgres:16-alpine
      servicePorts:
        - 5432
      vars:
        POSTGRES_USER: "app"
        POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
        POSTGRES_DB: "app"
      volumes:
        - name: fractional-crm-postgres-data
          size: 10Gi
          mountPath: /var/lib/postgresql
```
<!-- nexlayer:end -->

## Build History
<!-- nexlayer:section agent-managed=build_history -->
| Date | Status | Notes |
|------|--------|-------|
| 2026-07-13T17:07:23Z | analyzed | initial repo analysis |
| 2026-07-13T17:10:16Z | success | deployed https://flamboyant-goshawk-fractional-crm.cloud.nexlayer.ai |
<!-- nexlayer:end -->
