"""FastAPI application factory for the CRM web layer."""
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from fractional_crm.web.auth import router as auth_router, require_session, session_secret
from fractional_crm.web.pages import router as pages_router
from fractional_crm.web.pages_clients import router as clients_pages_router
from fractional_crm.web.routers.clients import router as clients_router
from fractional_crm.web.routers.engagements import router as engagements_router
from fractional_crm.web.routers.interactions import router as interactions_router
from fractional_crm.web.routers.teams import router as teams_router
from fractional_crm.web.routers.integrations import router as integrations_router
from fractional_crm.web.routers.reporting import router as reporting_router
from fractional_crm.web.routers.csv_routes import router as csv_router

_STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """Create the FastAPI app: signed sessions, static assets, public /health + auth, gated UI + API."""
    app = FastAPI()
    # Signed session cookie backs single-user passcode auth (CRB-28).
    app.add_middleware(SessionMiddleware, secret_key=session_secret())
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/health")
    def health() -> dict:
        """Public liveness probe returning {"status": "ok"}."""
        return {"status": "ok"}

    # Public: login/logout live in the auth router.
    app.include_router(auth_router)

    # Gated server-rendered UI pages.
    gated = [Depends(require_session)]
    app.include_router(pages_router)  # dashboard "/" self-gates per route
    app.include_router(clients_pages_router, dependencies=gated)

    # Every JSON API router requires an authenticated session.
    app.include_router(clients_router, dependencies=gated)
    app.include_router(engagements_router, dependencies=gated)
    app.include_router(interactions_router, dependencies=gated)
    app.include_router(teams_router, dependencies=gated)
    app.include_router(integrations_router, dependencies=gated)
    app.include_router(reporting_router, dependencies=gated)
    app.include_router(csv_router, dependencies=gated)
    return app


app = create_app()
