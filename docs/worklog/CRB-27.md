# CRB-27 — CSV import/export API

**What was built**
`web/routers/csv_routes.py` under `/api/clients/csv`: `GET /export` (text/csv attachment via the
existing `export_clients_csv`) and `POST /import` (multipart `UploadFile`, 5 MB cap -> 413, JSON vs
CSV by filename, via the existing `ClientImporter`, returning `{imported, errors}`; malformed -> 400).

**Design note**
Nested under `/api/clients/csv/` (not `/api/clients/export`) to avoid colliding with the clients
router's `/{email}` route.

**Follow-up (flagged, not done here)**
The CRB-27 spec assumed CSV formula-injection escaping was already in the domain — it is NOT.
`export_clients_csv` writes values raw. Hardening (prefix `= + - @` cells with `'`) should be a small
domain change to `csv_io.py` + a test, tracked separately (relates to docs/SECURITY_REVIEW.md).

**How it was built (the loop)**
- qwen2.5-coder-7b via aider (router + app wiring), zero bounces. Hardest endpoint so far (multipart +
  size cap + JSON/CSV sniff) — the precise contract carried it.

**Test coverage**
- export headers + body; import CSV (mixed valid/invalid -> per-row errors); import JSON; oversize 413.
  Full suite green.
