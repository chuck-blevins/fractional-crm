# Security & Quality Review — fractional-crm (CRB-18)

Reviewer: Claude (orchestrator). Scope: the full `src/fractional_crm` package and its
tests. This review answers CRB-18 ("is this application well built and secure?").

## Executive summary

The domain and persistence code is sound (parameterized SQL, safe parsing, disciplined
input validation). Two classes of problem were found and **fixed in this PR**: (1) the
project's own test suite did not run — three "Done" features had no implementation on
`main` — and (2) the passcode/token auth used fast hashing and non-constant-time
comparisons. After the fixes the full suite is green (202 tests).

## Findings

| # | Severity | Area | Status |
|---|----------|------|--------|
| 1 | Critical | Broken test suite / hollow "Done" tickets | Fixed |
| 2 | High | Weak passcode hashing (fast hash on low-entropy PINs) | Fixed |
| 3 | Medium | Timing-unsafe passcode comparison | Fixed |
| 4 | Low | Timing-unsafe verification-token comparison | Fixed |
| 5 | Info | Residual risks (below) | Documented |

### 1. Critical — broken suite / hollow "Done" (Fixed)
`tests/test_csv_io.py`, `tests/test_cli.py`, `tests/test_sso.py`, and
`tests/test_integration.py` imported modules (`csv_io`, `cli`, `sso`, `integration`)
that did not exist on `main`. `pytest` failed at collection, so **the suite never ran
green** even though CRB-7 (SSO), CRB-15 (CSV) and CRB-16 (CLI) were marked Done in Linear.
The feature *tests* were merged but the feature *code* was not.
Fix: implemented all four modules to their existing specs. Suite now collects and passes
(202 tests). Process recommendation: the merge gate must require the FULL suite to
collect+pass on `main` *after* merge before a ticket is marked Done.

### 2. High — weak passcode hashing (Fixed)
`passcode.py` hashed 4–8 digit PINs with a single `sha256(salt + pin)`. A leaked store
is brute-forceable in milliseconds (10^4–10^8 space, fast hash).
Fix: `pbkdf2_hmac("sha256", pin, salt, 200_000)`.

### 3. Medium — timing-unsafe passcode compare (Fixed)
Authentication compared digests with `==`. Fix: `hmac.compare_digest`.

### 4. Low — timing-unsafe token compare (Fixed)
`verification.py` compared tokens with `!=`. Fix: `hmac.compare_digest`.
(`sso.py`, added here, verifies the HMAC assertion with `compare_digest` and checks the
signature before trusting any claim.)

## Reviewed and found OK
- **SQL injection:** all `sqlite_repository` queries use `?` placeholders. Clean.
- **Deserialization:** `importer.import_json` uses `json.loads` (no `eval`).
- **Command injection:** the CLI is argv-based; tests invoke it via `subprocess.run`
  with a list and no `shell=True`; domain validators run on every input.

## Residual risks / recommendations (not fixed here)
- **CSV formula injection:** `export_clients_csv` is intentionally lossless (round-trip
  stable), so leading `= + - @` in a field are preserved. If exported CSVs are opened
  directly in a spreadsheet, those could execute. Mitigate at the spreadsheet-consumption
  boundary, or add an opt-in "safe export" that prefixes risky cells.
- **Passcode entropy:** 4–8 digit PINs are inherently weak; add rate-limiting/lockout at
  the application layer (outside this domain library).
- **Token TTL:** email-verification and SSO tokens do not expire; add expiry.
- **AuthZ:** `team.py` models roles but nothing enforces them; there is no RBAC layer.
- **Secret handling:** `GmailSSO` takes the signing secret in-process; source it from a
  secret store in production, never a literal.
