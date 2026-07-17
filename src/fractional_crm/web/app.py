"""FastAPI application factory for the CRM web layer."""
from fastapi import Depends, FastAPI
from starlette.middleware.sessions import SessionMiddleware

from fractional_crm.web.auth import router as auth_router, require_session, session_secret
from fractional_crm.web.routers.clients import router as clients_router
from fractional_crm.web.routers.engagements import router as engagements_router
from fractional_crm.web.routers.interactions import router as interactions_router
from fractional_crm.web.routers.teams import router as teams_router
from fractional_crm.web.routers.integrations import router as integrations_router
from fractional_crm.web.routers.reporting import router as reporting_router
from fractional_crm.web.routers.csv_routes import router as csv_router


def create_app() -> FastAPI:
    """Create the FastAPI app: signed sessions, public /health + auth, gated API routers."""
    app = FastAPI()
    # Signed session cookie backs single-user passcode auth (CRB-28).
    app.add_middleware(SessionMiddleware, secret_key=session_secret())

    @app.get("/health")
    def health() -> dict:
        """Public liveness probe returning {"status": "ok"}."""
        return {"status": "ok"}

    # Public: login/logout live in the auth router; its "/" home is self-gated.
    app.include_router(auth_router)

    # Every JSON API router requires an authenticated session.
    gated = [Depends(require_session)]
    app.include_router(clients_router, dependencies=gated)
    app.include_router(engagements_router, dependencies=gated)
    app.include_router(interactions_router, dependencies=gated)
    app.include_router(teams_router, dependencies=gated)
    app.include_router(integrations_router, dependencies=gated)
    app.include_router(reporting_router, dependencies=gated)
    app.include_router(csv_router, dependencies=gated)
    return app


app = create_app()
