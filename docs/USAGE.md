# fractional-crm — User Guide

fractional-crm helps a fractional COO/CPO track **clients**, the **engagements** you
have with them, **interactions** (touchpoints), your **team**, third-party
**integrations**, and simple **reporting**. It ships a command-line interface and a
Python API. All data validation happens in the domain models, so bad input is rejected
consistently whether it arrives via the CLI, a CSV import, or code.

## Contents
- [Command-line interface](#command-line-interface)
- [Clients](#clients)
- [Engagements](#engagements)
- [Storing data (repositories)](#storing-data-repositories)
- [Interactions](#interactions)
- [Reporting](#reporting)
- [CSV import / export](#csv-import--export)
- [Teams](#teams)
- [Integrations](#integrations)
- [Authentication](#authentication)
- [Data reference](#data-reference)
- [Security](#security)

## Command-line interface
The CLI is a thin wrapper over the domain models and the SQLite store. Every command
takes `--db <path>`; the database file is created on first use and persists between runs.

```bash
# Clients
python -m fractional_crm.cli --db crm.db client add \
  --name "Ada Lovelace" --company "Acme" --email ada@acme.io \
  --status active --engagement-type coo
python -m fractional_crm.cli --db crm.db client list

# Engagements
python -m fractional_crm.cli --db crm.db engagement add \
  --client-email ada@acme.io --role coo --monthly-rate 5000 \
  --start-date 2026-01-01 --status active [--end-date 2026-06-30]
python -m fractional_crm.cli --db crm.db engagement list
```
Invalid input (bad email, unknown status/role, duplicate key) exits non-zero and prints
an `error:` line to stderr.

## Clients
```python
from fractional_crm.client import Client

c = Client(name="Ada Lovelace", company="Acme", email="ada@acme.io",
           status="active", engagement_type="coo")
c.transition_to("paused")   # enforces the allowed status lifecycle
```
Validation: non-empty name, valid email, `status` and `engagement_type` from the allowed
sets (below). `transition_to(new_status)` permits only
`prospect→active`, `active→paused`, `paused→active`, `active→closed`, `paused→closed`;
any other move raises `ValueError` and leaves the status unchanged.

## Engagements
```python
from fractional_crm.engagement import Engagement

e = Engagement(client_email="ada@acme.io", role="coo", monthly_rate=5000,
               start_date="2026-01-01", status="active", end_date="2026-06-30")
```
Validation: valid email; `role` in the allowed set; `monthly_rate > 0`; `start_date` and
optional `end_date` are ISO date strings (kept verbatim); if present, `end_date >= start_date`.

## Storing data (repositories)
Two interchangeable repositories expose the same interface — `add`, `get`, `list`,
`update`, `delete`. `add` raises `ValueError` on a duplicate key; the others raise
`KeyError` when the key is missing.

```python
from fractional_crm.repository import ClientRepository            # in-memory
from fractional_crm.sqlite_repository import SqliteClientRepository, SqliteEngagementRepository

repo = ClientRepository()
repo.add(c); repo.get("ada@acme.io"); repo.list()

db = SqliteClientRepository("crm.db")   # ":memory:" by default
db.add(c); db.close()
```
Clients are keyed by `email`, engagements by `client_email`.

## Interactions
```python
from fractional_crm.interaction import Interaction
from fractional_crm.interaction_log import InteractionLog

log = InteractionLog()
log.add(Interaction(client_email="ada@acme.io", date="2026-02-01",
                    kind="call", summary="Kickoff call"))
log.list_for_client("ada@acme.io")   # newest first
```
`kind` is one of `call`, `email`, `meeting`, `note`; `date` is an ISO date; `summary`
must be non-empty.

## Reporting
```python
from fractional_crm.reporting import active_engagements, monthly_run_rate

active_engagements(engagements)   # only status == "active", input order preserved
monthly_run_rate(engagements)     # sum of monthly_rate over active engagements (0 if none)
```

## CSV import / export
```python
from fractional_crm.csv_io import export_clients_csv, import_clients_csv

text = export_clients_csv(repo)          # header: name,company,email,status,engagement_type
clients = import_clients_csv(text)       # validated Client objects; round-trip stable
```
Import raises `ValueError` on a wrong header, wrong column count, or any value the Client
validator rejects. A repository-aware importer that also accepts JSON and collects
per-row errors is available as `fractional_crm.importer.ClientImporter`.

## Teams
```python
from fractional_crm.team import Team, TeamMember

team = Team("Delivery")
team.add_member(TeamMember(name="Ada", email="ada@acme.io", role="admin"))
team.members_with_role("admin")
```
Member roles: `admin`, `member`, `guest`.

## Integrations
```python
from fractional_crm.integration import Integration, IntegrationRegistry

reg = IntegrationRegistry()
reg.connect(Integration(provider="slack", external_id="T012AB3CD"))
reg.get("slack").mark_synced("2026-07-11T12:00:00")
reg.disconnect("slack")
```
Providers: `slack`, `github`, `gitlab`, `figma`, `intercom`, `zendesk`.
Statuses: `connected`, `disconnected`, `error`.

## Authentication
Three independent mechanisms, each keyed per client:

```python
from fractional_crm.passcode import PasscodeAuth          # 4-8 digit PIN
from fractional_crm.verification import EmailVerification  # email confirmation token
from fractional_crm.sso import GmailSSO                    # Gmail (Google) SSO assertion

auth = PasscodeAuth(); auth.set_passcode(c, "824617"); auth.authenticate(c, "824617")
ev = EmailVerification(); tok = ev.request(c); ev.verify(c, tok); ev.is_verified(c)
sso = GmailSSO("app-signing-secret"); sso.link(c, "google-sub-123")
```
Passcodes are stored only as a salted PBKDF2 hash; all secret comparisons are
constant-time. See the [security review](SECURITY_REVIEW.md) for details and residual risks.

## Data reference
| Field | Allowed values |
|-------|----------------|
| Client `status` | `prospect`, `active`, `paused`, `closed` |
| Client / Engagement `engagement_type` / `role` | `coo`, `cpo`, `advisor` |
| Engagement `status` | `proposed`, `active`, `completed`, `cancelled` |
| Interaction `kind` | `call`, `email`, `meeting`, `note` |
| Team member `role` | `admin`, `member`, `guest` |
| Integration `provider` | `slack`, `github`, `gitlab`, `figma`, `intercom`, `zendesk` |
| Integration `status` | `connected`, `disconnected`, `error` |

## Security
See [docs/SECURITY_REVIEW.md](SECURITY_REVIEW.md) for the security review, the fixes
applied, and residual risks (CSV formula-injection considerations, PIN entropy, token
expiry, authorization, and secret handling).
