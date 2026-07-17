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

---

# Security Review — web auth surface (2026-07-17)

Reviewer: Claude (orchestrator). Scope: the CRB-28 authentication surface **as merged to `main`** —
`web/auth.py`, the `web/app.py` middleware + router wiring, `web/pages.py` gating, `tests/web/conftest.py`
— plus the session cookie as actually issued at runtime. This is a **retro-review**: CRB-28/29/30 were
merged with no recorded review decision.

Method: code read **plus an empirical probe** against the built app (TestClient). Every finding and every
"found OK" below was confirmed by observed behaviour, not by reading alone.

## Executive summary

The gate itself is sound. Every `/api` route 401s and every UI page 303-redirects to `/login` when
unauthenticated; there is **no bypass** when `CRM_PASSCODE_HASH` is unset or malformed; the passcode is
PBKDF2-salted and compared in constant time; the cookie is HttpOnly + SameSite=Lax.

Five findings. **Four are fixed in this PR** (2, 3, 4, 5). **Finding 1 — no rate limiting on `/login` —
is the one that matters** and is tracked as **CRB-39**: it is the only thing standing between a guessed
passcode and the entire application.

Nothing here was a live vulnerability at review time — the app is not deployed (CRB-19/Nexlayer is broken
and 503s). **Findings 1 and 2 must be closed before CRB-35 puts this on the internet.**

## Findings

| # | Severity | Area | Status |
|---|----------|------|--------|
| 1 | High | No rate limiting or lockout on `/login` | **Open — CRB-39** |
| 2 | High (pre-deploy) | Session cookie issued without `Secure` | Fixed |
| 3 | Medium | Ephemeral-secret fallback fails open on unset `CRM_ENV` | Fixed |
| 4 | Low | Latent reflected XSS in `_login_html` | Fixed |
| 5 | Low | Inconsistent gating on `pages_router` (latent public route) | Fixed |

### 1. High — no rate limiting on `/login` (OPEN — CRB-39)
Observed: 12 consecutive wrong passcodes returned HTTP 200 each — no 429, no lockout, no backoff — and
`grep` finds no throttle anywhere in `src/`. The whole application is protected by one passcode and
nothing limits guessing it. The only brake is PBKDF2's ~134 ms/attempt (~7/sec per connection), which
parallelises away trivially.

Second-order: that same 134 ms is *unauthenticated* CPU. Each anonymous `POST /login` costs 200k SHA-256
iterations, so the login endpoint doubles as a cheap CPU-exhaustion DoS vector — which is also why simply
raising the iteration count is **not** a fix. Rate limit first, then revisit iterations.

### 2. High (pre-deploy) — session cookie without `Secure` (Fixed)
Observed: `session=...; path=/; Max-Age=1209600; httponly; samesite=lax` — no `secure`.
`SessionMiddleware` was added with bare defaults (`https_only=False`), so the session cookie would cross
plaintext HTTP once deployed.
**Fix:** `https_only=is_production()`. Verified: `CRM_ENV=production` now issues `secure`; dev/test does
not (TestClient's http transport would otherwise drop the cookie).

### 3. Medium — fail-open secret fallback (Fixed)
`session_secret()` raised only when `CRM_ENV == "production"` *exactly*. Any other value — including
unset, or a typo like `prod` — silently returned a random per-process secret. Deployed that way with more
than one uvicorn worker, each worker signs with a different key: sessions fail intermittently with no
error, and a restart logs everyone out.
**Fix:** inverted the default. `is_production()` returns True unless `CRM_ENV` explicitly names a dev/test
environment, so a forgotten variable now raises at startup. Verified: unset, `production`, and `typo-prod`
all raise; `dev` returns an ephemeral secret.
*Knock-on:* `app.py` built `app = create_app()` at import time, which under a fail-secure default would
demand production config just to import (breaking test collection). `app` is now built lazily via a module
`__getattr__` (PEP 562), preserving the documented `uvicorn fractional_crm.web.app:app` entrypoint.
Verified: import succeeds unconfigured; `.app` raises unconfigured; `.app` is cached across accesses.

### 4. Low — latent reflected XSS in `_login_html` (Fixed)
`banner = f'<p class="error" role="alert">{error}</p>'` interpolated `error` unescaped. Not exploitable as
merged — `error` is only ever `""` or the literal `"Incorrect passcode"` — but a loaded gun for the next
caller who echoes user input into it.
**Fix:** `html.escape(error)`. Verified: a raw `<script>` no longer survives.

### 5. Low — inconsistent gating on `pages_router` (Fixed)
Every router was gated at include level (`dependencies=[Depends(require_session)]`) **except**
`pages_router`, which was included with no dependencies and self-gated per route. `/` carried its own
dependency correctly, so nothing was exposed — but any page added without that decorator would be
silently public. CRB-31..34 add exactly those pages.
**Fix:** `pages_router` is gated at include level like every other router; the per-route dependency is
removed and the module docstring says not to reintroduce it. Verified: a new route added to `pages_router`
with no auth dependency now 303-redirects to `/login`.

## Reviewed and found OK (verified, not assumed)

- **No auth bypass.** `verify_passcode` returns False for `''`, `'$'`, `'garbage'`, `'aa$bb'` — an unset or
  corrupt `CRM_PASSCODE_HASH` denies rather than admits.
- **Gate coverage.** `/api/clients` → 401; `/clients` → 303 `/login`; `/` → 303 `/login`; `/health` → 200
  (public by design, leaks nothing).
- **Hashing.** PBKDF2-HMAC-SHA256, 200k iterations, fresh 16-byte salt per hash, `hmac.compare_digest`.
- **Cookie flags.** HttpOnly and SameSite=Lax present (Starlette sets HttpOnly unconditionally).
- **No user enumeration.** A failed login returns a generic message and HTTP 200.
- **No open redirect.** Successful login redirects to a hardcoded `/`.
- **Session rotates on login.**

## Residual risks / accepted (not fixed here)

- **CSRF rests entirely on `SameSite=Lax`** — no tokens. Adequate while every mutation is a POST (Lax
  withholds the cookie on cross-site POST). Revisit if `same_site` is ever relaxed to `none`.
- **14-day session** (`Max-Age=1209600`, Starlette default), no idle timeout. Accepted for a single-user
  personal CRM; revisit if the app ever grows users.
- **PBKDF2 at 200k vs OWASP's current 600k guidance.** Deliberately *not* raised: tripling it also triples
  the unauthenticated CPU cost described in finding 1. Sequence it after CRB-39 — rate limit first, then
  iterations.
- **No `__Host-` cookie prefix.** Would require `Secure` unconditionally, breaking dev over http.
- **SAST still not installed** (bandit/semgrep) — the "automated layer" of the two-layer security gate
  remains a manual review only. Carried over from the CRB-18 review above.
- **Reviewer independence.** This is a **self-review**: the same reviewer wrote the `app.py` wiring and
  finished `auth.py` during CRB-28. Findings 2, 3 and 5 were reviewer mistakes, not local-model output. An
  independent pass is worth more than this one.
