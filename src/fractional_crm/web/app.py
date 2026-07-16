"""FastAPI application factory for the CRM web layer."""
from fastapi import FastAPI

from fractional_crm.web.routers.clients import router as clients_router


def create_app() -> FastAPI:
    """Create the FastAPI app, register /health and the clients router."""
    app = FastAPI()

    @app.get("/health")
    def health() -> dict:
        """Public liveness probe returning {"status": "ok"}."""
        return {"status": "ok"}

    app.include_router(clients_router)
    return app


app = create_app()
