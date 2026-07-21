"""Global interactions feed page."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fractional_crm.sqlite_interaction_repository import SqliteInteractionRepository
from fractional_crm.web.deps import get_interaction_repo
from fractional_crm.web.templates import templates

router = APIRouter(prefix="/interactions")

@router.get("", response_class=HTMLResponse)
def interactions_list(request: Request,
                      repo: SqliteInteractionRepository = Depends(get_interaction_repo)) -> HTMLResponse:
    """Render the global interactions feed, newest first."""
    return templates.TemplateResponse(request, "interactions/index.html", {
        "interactions": repo.list_all(),
    })
