"""Server-rendered UI pages (accessible, HTMX-enhanced). All pages require a session."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from fractional_crm.web.auth import require_session
from fractional_crm.web.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(require_session)])
def dashboard(request: Request) -> HTMLResponse:
    """Render the authenticated dashboard shell (widgets are slotted in CRB-31)."""
    return templates.TemplateResponse(request, "index.html", {"title": "Dashboard"})
