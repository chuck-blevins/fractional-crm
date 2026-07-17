"""CRB-28: single-user passcode login and signed-session route protection.

Exposes passcode hashing helpers, a ``require_session`` dependency used to gate the
JSON API routers and UI pages, and a router providing ``/login`` and ``/logout``.
The domain stays framework-free; all web/auth glue lives here.
"""
import hashlib
import hmac
import html
import os
import secrets

from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

_PBKDF2_ITERATIONS = 200_000

#: CRM_ENV values that mark a NON-production run. Anything else — including unset — is
#: treated as production, so a forgotten env var fails secure instead of silently
#: weakening the app. See docs/SECURITY_REVIEW.md (2026-07-17, finding 3).
_DEV_ENVS = frozenset({"dev", "development", "test", "testing", "local"})


def is_production() -> bool:
    """Return True unless CRM_ENV explicitly names a dev/test environment.

    Fail-secure: an unset or unrecognised CRM_ENV is production. Callers use this to
    decide whether a session secret is mandatory and whether the session cookie is
    issued Secure (HTTPS-only).
    """
    return os.environ.get("CRM_ENV", "").strip().lower() not in _DEV_ENVS


def hash_passcode(passcode: str) -> str:
    """Hash a passcode as ``<salt_hex>$<pbkdf2_sha256_hex>`` (for CRM_PASSCODE_HASH)."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", passcode.encode(), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_passcode(passcode: str, stored: str) -> bool:
    """Return True iff ``passcode`` matches a ``<salt_hex>$<digest_hex>`` value, in constant time."""
    try:
        salt_hex, _, digest_hex = stored.partition("$")
        if not salt_hex or not digest_hex:
            return False
        recomputed = hashlib.pbkdf2_hmac("sha256", passcode.encode(), bytes.fromhex(salt_hex), _PBKDF2_ITERATIONS)
        return hmac.compare_digest(recomputed, bytes.fromhex(digest_hex))
    except ValueError:
        return False


def require_session(request: Request) -> None:
    """Gate a route: allow if the session is authenticated, else 401 for /api or redirect pages to /login."""
    if request.session.get("authenticated"):
        return
    if request.url.path.startswith("/api"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    raise HTTPException(status_code=303, headers={"Location": "/login"})


def _login_html(error: str = "") -> str:
    """Return the login page HTML, showing an error banner when ``error`` is non-empty.

    ``error`` is HTML-escaped. Today it is only ever a module literal, but escaping stops
    this becoming reflected XSS the moment a caller passes user-controlled text.
    See docs/SECURITY_REVIEW.md (2026-07-17, finding 4).
    """
    banner = f'<p class="error" role="alert">{html.escape(error)}</p>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Sign in</title></head>
<body>
  <main>
    <h1>Sign in</h1>
    {banner}
    <form method="post" action="/login">
      <label for="passcode">Passcode</label>
      <input id="passcode" name="passcode" type="password" required>
      <button type="submit">Log in</button>
    </form>
  </main>
</body>
</html>"""


def session_secret() -> str:
    """Return the session signing secret from CRM_SESSION_SECRET.

    Required in production. Only when CRM_ENV explicitly marks a dev/test run does this
    fall back to an ephemeral per-process secret. Because :func:`is_production` treats an
    unset CRM_ENV as production, forgetting the variable raises at startup rather than
    silently starting with a per-worker secret (which breaks sessions across workers).
    See docs/SECURITY_REVIEW.md (2026-07-17, finding 3).
    """
    secret = os.environ.get("CRM_SESSION_SECRET")
    if secret:
        return secret
    if is_production():
        raise RuntimeError(
            "CRM_SESSION_SECRET is required. Set it, or set CRM_ENV to one of "
            f"{sorted(_DEV_ENVS)} to use an ephemeral dev/test secret."
        )
    return secrets.token_hex(32)


router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_form() -> str:
    """Render the empty login form (public)."""
    return _login_html()


@router.post("/login", response_class=HTMLResponse)
def login(request: Request, passcode: str = Form(...)) -> Response:
    """Verify the passcode; on success set the session and redirect to /, else re-render with a generic error."""
    stored = os.environ.get("CRM_PASSCODE_HASH", "")
    if verify_passcode(passcode, stored):
        request.session["authenticated"] = True
        return RedirectResponse("/", status_code=303)
    # Generic error only — never reveal whether input was close (no user enumeration).
    return HTMLResponse(_login_html("Incorrect passcode"), status_code=200)


@router.post("/logout")
def logout(request: Request) -> Response:
    """Clear the session and redirect to the login page."""
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
