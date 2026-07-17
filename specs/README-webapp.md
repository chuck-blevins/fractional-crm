# Web app backlog: FastAPI + SQLite + Jinja2/HTMX (CRB-20 … CRB-38)

Goal: make the existing (tested) Python CRM **web-based and accessible**, built primarily by
the local-LLM + Aider loop. We add a FastAPI + Jinja2/HTMX layer over `src/fractional_crm/`
and deploy one small container to Nexlayer. The domain is reused, not rewritten.

Each story = one `specs/task-crbN.md` + `crb-N-*` branch + PR to `main`, built test-first with
FastAPI TestClient. DoD for every story: comprehensive docstrings/annotation + a
`docs/worklog/CRB-N.md` summary (see `.agent/conventions.md`). All web code lives under
`src/fractional_crm/web/`; the domain stays framework-free.

## Sequence & dependencies

| # | Story | Depends on |
|---|-------|-----------|
| CRB-20 | FastAPI app scaffold: app factory, `/health`, TestClient harness, deps | — |
| CRB-21 | Config + SQLite wiring (repo dependency, temp-DB test fixture) | CRB-20 |
| CRB-22 | Clients JSON API (CRUD + status transition) | CRB-21 |
| CRB-23 | Engagements JSON API | CRB-21 |
| CRB-24 | Interactions JSON API (log + list newest-first) | CRB-21 |
| CRB-25 | Teams + Integrations JSON API | CRB-21 |
| CRB-26 | Reporting API (active count, monthly run-rate) | CRB-21 |
| CRB-27 | CSV import/export API (+ formula-injection escaping) | CRB-22 |
| CRB-28 | Session login (passcode auth) + route protection | CRB-20 |
| CRB-29 | Base layout + accessible nav (Jinja2) | CRB-28 |
| CRB-30 | Clients UI (list/create/edit/status; HTMX) | CRB-22, CRB-29 |
| CRB-31 | Engagements UI + reporting dashboard | CRB-23, CRB-26, CRB-29 |
| CRB-32 | Interactions timeline UI | CRB-24, CRB-29 |
| CRB-33 | Teams + Integrations UI | CRB-25, CRB-29 |
| CRB-34 | CSV import/export UI | CRB-27, CRB-29 |
| CRB-35 | Dockerfile + nexlayer.yaml (SQLite volume) — real deploy config | CRB-20 |
| CRB-36 | GitHub Actions CI (pytest gate on PRs to main) | CRB-20 |
| CRB-37 | README/USAGE update for the web app | most |
| CRB-38 | Accessibility pass (WCAG 2.1 AA audit + fixes) | UI stories |

CRB-19 ("Deploy via NexLayer") is the umbrella deploy issue; CRB-35 produces the real
config that supersedes the earlier hallucinated one (PR #13).

## Reviewer notes (local qwen2.5-coder-7b)
JSON-API stories (CRB-22…CRB-27) are the model's sweet spot: a failing TestClient test + an
endpoint over the existing domain. Scaffold/auth/deploy (CRB-20, 28, 35, 36) may need a tighter
spec or a reviewer finish — record any finish in `.agent/lessons.md`. UI stories need a
scaffolded template-assertion test per story to keep the model on-rails.
