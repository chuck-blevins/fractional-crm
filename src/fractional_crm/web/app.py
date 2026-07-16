"""FastAPI application factory for the CRM web layer."""
from fastapi import FastAPI

from fractional_crm.web.routers.clients import router as clients_router
from fractional_crm.web.routers.engagements import router as engagements_router
from fractional_crm.web.routers.interactions import router as interactions_router


def create_app() -> FastAPI:
    """Create the FastAPI app, register /health and the clients router."""
    app = FastAPI()

    @app.get("/health")
    def health() -> dict:
        """Public liveness probe returning {"status": "ok"}."""
        return {"status": "ok"}

    app.include_router(clients_router)
    app.include_router(engagements_router)
    app.include_router(interactions_router)
    return app


app = create_app()
