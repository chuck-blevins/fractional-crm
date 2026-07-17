"""FastAPI application factory for the CRM web layer."""
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from fractional_crm.web.auth import (
    router as auth_router,
    is_production,
    require_session,
    session_secret,
)
from fractional_crm.web.pages import router as pages_router
from fractional_crm.web.ratelimit import limiter_from_env
from fractional_crm.web.pages_clients import router as clients_pages_router
from fractional_crm.web.pages_engagements import router as engagements_pages_router
from fractional_crm.web.pages_client_detail import router as client_detail_pages_router
from fractional_crm.web.routers.clients import router as clients_router
from fractional_crm.web.routers.engagements import router as engagements_router
from fractional_crm.web.routers.interactions import router as interactions_router
from fractional_crm.web.routers.teams import router as teams_router
from fractional_crm.web.routers.integrations import router as integrations_router
from fractional_crm.web.routers.reporting import router as reporting_router
from fractional_crm.web.routers.csv_routes import router as csv_router

_STATIC_DIR = Path(__file__).parent / "static"

#: Cached instance backing the lazy module-level ``app`` attribute (see __getattr__).
_app = None


def create_app() -> FastAPI:
    """Create the FastAPI app: signed sessions, static assets, public /health + auth, gated UI + API."""
    app = FastAPI()
    # Signed session cookie backs single-user passcode auth (CRB-28).
    # https_only adds the Secure flag in production so the cookie never crosses plaintext
    # HTTP; dev/test runs stay on http. See docs/SECURITY_REVIEW.md (2026-07-17, finding 2).
    app.add_middleware(
        SessionMiddleware,
        secret_key=session_secret(),
        https_only=is_production(),
        same_site="lax",
    )
    # CRB-39: per-app login limiter, so each app instance (and each test) gets clean state.
    app.state.login_limiter = limiter_from_env()
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/health")
    def health() -> dict:
        """Public liveness probe returning {"status": "ok"}."""
        return {"status": "ok"}

    # Public: login/logout live in the auth router.
    app.include_router(auth_router)

    # Everything below is gated at INCLUDE level, uniformly. A route can therefore never
    # become accidentally public by omitting a per-route dependency — the previous
    # per-route gating on pages_router was a latent trap for CRB-31..34, which add pages
    # to it. See docs/SECURITY_REVIEW.md (2026-07-17, finding 5).
    gated = [Depends(require_session)]

    # Gated server-rendered UI pages.
    app.include_router(pages_router, dependencies=gated)
    app.include_router(clients_pages_router, dependencies=gated)
    app.include_router(client_detail_pages_router, dependencies=gated)  # GET /clients/{email}
    app.include_router(engagements_pages_router, dependencies=gated)

    # Every JSON API router requires an authenticated session.
    app.include_router(clients_router, dependencies=gated)
    app.include_router(engagements_router, dependencies=gated)
    app.include_router(interactions_router, dependencies=gated)
    app.include_router(teams_router, dependencies=gated)
    app.include_router(integrations_router, dependencies=gated)
    app.include_router(reporting_router, dependencies=gated)
    app.include_router(csv_router, dependencies=gated)
    return app


def __getattr__(name: str) -> FastAPI:
    """Lazily build the module-level ``app`` used by ``uvicorn fractional_crm.web.app:app``.

    Building it at import time would make importing this module require a full production
    config (a session secret) before anything — including test collection — could run.
    PEP 562 module ``__getattr__`` keeps the documented ``:app`` entrypoint working while
    deferring construction to first access.
    """
    if name == "app":
        global _app
        if _app is None:
            _app = create_app()
        return _app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
