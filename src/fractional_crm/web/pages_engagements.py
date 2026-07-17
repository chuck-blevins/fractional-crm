"""Engagements UI: accessible list (filterable by client) + create/edit forms.

Reuses the domain Engagement + repository. HTMX enhances create without full reloads,
but every action also works as a plain form POST -> redirect (progressive enhancement).
Handlers are sync `def` to stay on the sqlite repo's thread (see .agent/lessons.md).
"""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from fractional_crm.engagement import ROLES, STATUSES, Engagement
from fractional_crm.sqlite_repository import SqliteEngagementRepository
from fractional_crm.web.deps import get_engagement_repo
from fractional_crm.web.errors import not_found
from fractional_crm.web.templates import templates

router = APIRouter(prefix="/engagements")


def _rows(repo: SqliteEngagementRepository, client_email: str | None = None) -> list[dict]:
    """Return [{engagement}] for every stored engagement (filtered by client_email if provided)."""
    return [{"engagement": e} for e in repo.list() if client_email is None or e.client_email == client_email]


def _list_response(request: Request, repo: SqliteEngagementRepository, *, client_email: str | None = None,
                   template: str = "engagements/list.html", status_code: int = 200) -> HTMLResponse:
    """Render the engagements list (full page) or the `_table.html` fragment for HTMX swaps."""
    return templates.TemplateResponse(request, template, {"rows": _rows(repo, client_email)}, status_code=status_code)


def _form_response(request: Request, *, mode: str, action: str, form: dict, error: str | None,
                   client_email_readonly: bool, status_code: int = 200) -> HTMLResponse:
    """Render the create/edit engagement form (optionally with an error summary)."""
    return templates.TemplateResponse(request, "engagements/form.html", {
        "mode": mode, "action": action, "form": form, "error": error,
        "roles": ROLES, "statuses": STATUSES, "client_email_readonly": client_email_readonly,
    }, status_code=status_code)


@router.get("", response_class=HTMLResponse)
def list_engagements(request: Request, repo: SqliteEngagementRepository = Depends(get_engagement_repo),
                     client_email: str | None = None) -> HTMLResponse:
    """Render the engagements table with per-row controls."""
    return _list_response(request, repo, client_email=client_email)


@router.get("/new", response_class=HTMLResponse)
def new_engagement_form(request: Request) -> HTMLResponse:
    """Render the empty create-engagement form."""
    return _form_response(request, mode="create", action="/engagements", form={}, error=None, client_email_readonly=False)


@router.post("")
def create_engagement(
    request: Request,
    client_email: str = Form(...),
    role: str = Form(...),
    monthly_rate: float = Form(...),
    start_date: str = Form(...),
    status: str = Form(...),
    end_date: str = Form(""),
    repo: SqliteEngagementRepository = Depends(get_engagement_repo),
) -> Response:
    """Create an engagement; re-render the form with an error (200) on invalid/duplicate, else redirect to /engagements."""
    fields = {"client_email": client_email, "role": role, "monthly_rate": monthly_rate,
              "start_date": start_date, "status": status, "end_date": end_date or None}
    try:
        repo.add(Engagement(**fields))
    except ValueError as e:
        return _form_response(request, mode="create", action="/engagements", form=fields, error=str(e), client_email_readonly=False)
    if request.headers.get("HX-Request"):
        return _list_response(request, repo, template="engagements/_table.html")
    return RedirectResponse("/engagements", status_code=303)


@router.get("/{client_email}/edit", response_class=HTMLResponse)
def edit_engagement_form(request: Request, client_email: str,
                         repo: SqliteEngagementRepository = Depends(get_engagement_repo)) -> HTMLResponse:
    """Render the edit form for one engagement; 404 if missing."""
    try:
        e = repo.get(client_email)
    except KeyError as e:
        raise not_found(str(e))
    fields = {"client_email": client_email, "role": e.role, "monthly_rate": e.monthly_rate,
              "start_date": e.start_date, "status": e.status, "end_date": e.end_date}
    return _form_response(request, mode="edit", action=f"/engagements/{client_email}", form=fields, error=None, client_email_readonly=True)


@router.post("/{client_email}")
def update_engagement(
    request: Request, client_email: str,
    role: str = Form(...),
    monthly_rate: float = Form(...),
    start_date: str = Form(...),
    status: str = Form(...),
    end_date: str = Form(""),
    repo: SqliteEngagementRepository = Depends(get_engagement_repo),
) -> Response:
    """Update an engagement (client_email is the immutable key); re-render on error, else redirect to /engagements."""
    fields = {"client_email": client_email, "role": role, "monthly_rate": monthly_rate,
              "start_date": start_date, "status": status, "end_date": end_date or None}
    try:
        repo.update(Engagement(**fields))
    except ValueError as e:
        return _form_response(request, mode="edit", action=f"/engagements/{client_email}", form=fields, error=str(e), client_email_readonly=True)
    except KeyError as e:
        raise not_found(str(e))
    if request.headers.get("HX-Request"):
        return _list_response(request, repo, template="engagements/_table.html")
    return RedirectResponse("/engagements", status_code=303)
