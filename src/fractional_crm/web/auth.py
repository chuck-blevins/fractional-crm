"""CRB-28: single-user passcode login and signed-session route protection.

Exposes passcode hashing helpers, a ``require_session`` dependency used to gate the
JSON API routers, and a small router providing ``/login``, ``/logout`` and a gated
home page. The domain stays framework-free; all web/auth glue lives here.
"""
import hashlib
import hmac
import os
import secrets

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

_PBKDF2_ITERATIONS = 200_000


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
    """Return the login page HTML, showing an error banner when `error` is non-empty."""
    banner = f'<p class="error" role="alert">{error}</p>' if error else ""
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

    Required in production (CRM_ENV=production); otherwise falls back to an
    ephemeral per-process secret so dev/test runs work without configuration.
    """
    secret = os.environ.get("CRM_SESSION_SECRET")
    if secret:
        return secret
    if os.environ.get("CRM_ENV") == "production":
        raise RuntimeError("CRM_SESSION_SECRET is required in production")
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


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(require_session)])
def home() -> str:
    """Authenticated landing page (placeholder until the CRB-29+ UI lands)."""
    return """
    <main>
      <h1>Fractional CRM</h1>
      <p>You are signed in.</p>
      <form method='post' action='/logout'>
        <button type='submit'>Log out</button>
      </form>
    </main>
    """
