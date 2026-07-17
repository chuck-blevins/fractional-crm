"""Server-rendered UI pages (accessible, HTMX-enhanced). All pages require a session.

Gating is applied once, at include time in ``app.py`` (``dependencies=[Depends(require_session)]``),
so every route in this router is authenticated by construction. Do NOT add per-route
auth dependencies here — uniform include-level gating is what stops a new page from
being accidentally public. See docs/SECURITY_REVIEW.md (2026-07-17, finding 5).
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from fractional_crm.web.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """Render the authenticated dashboard shell (widgets are slotted in CRB-31)."""
    return templates.TemplateResponse(request, "index.html", {"title": "Dashboard"})
