# fractional-crm

A lightweight CRM for a fractional COO/CPO practice — manage clients, engagements,
interactions, teams, and integrations, with a command-line interface and a small,
well-tested Python API.

- **User guide:** [docs/USAGE.md](docs/USAGE.md)
- **Security review:** [docs/SECURITY_REVIEW.md](docs/SECURITY_REVIEW.md)

## Quick start

```bash
# create a client and list it (SQLite-backed, one file per database)
python -m fractional_crm.cli --db crm.db client add \
  --name "Ada Lovelace" --company "Acme" --email ada@acme.io \
  --status active --engagement-type coo
python -m fractional_crm.cli --db crm.db client list
```

## Tests

```bash
python -m pytest -q
```
