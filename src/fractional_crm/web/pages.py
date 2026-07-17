"""Server-rendered UI pages (accessible, HTMX-enhanced). All pages require a session.

Gating is applied once, at include time in ``app.py`` (``dependencies=[Depends(require_session)]``),
so every route in this router is authenticated by construction. Do NOT add per-route
auth dependencies here — uniform include-level gating is what stops a new page from
being accidentally public. See docs/SECURITY_REVIEW.md (2026-07-17, finding 5).
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from fractional_crm.reporting import active_engagements, monthly_run_rate
from fractional_crm.sqlite_repository import SqliteEngagementRepository
from fractional_crm.web.deps import get_engagement_repo
from fractional_crm.web.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request,
              repo: SqliteEngagementRepository = Depends(get_engagement_repo)) -> HTMLResponse:
    """Render the dashboard with CRB-31 overview widgets (active engagements + monthly run-rate)."""
    engagements = repo.list()
    return templates.TemplateResponse(request, "index.html", {
        "title": "Dashboard",
        "active_count": len(active_engagements(engagements)),
        "monthly_run_rate": monthly_run_rate(engagements),
    })
