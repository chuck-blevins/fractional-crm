import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fractional_crm.integration import PROVIDERS, Integration
from fractional_crm.sqlite_integration_repository import SqliteIntegrationRepository
from fractional_crm.web.deps import get_integration_repo
from fractional_crm.web.errors import not_found
from fractional_crm.web.templates import templates

router = APIRouter(prefix="/integrations")

def now_iso() -> str:
    """Return the current local time as an ISO-8601 string.

    A seam, not a convenience: the JSON API takes a caller-supplied timestamp, but a
    "sync now" button must stamp server-side. Tests replace this to pin the clock.
    """
    return datetime.datetime.now().isoformat(timespec="seconds")

def _rows(repo):
    """Return one row per known provider, with its Integration or None."""
    connected = {i.provider: i for i in repo.list()}
    return [{"provider": p, "integration": connected.get(p)} for p in PROVIDERS]

def _list_response(request, repo, *, error=None, form=None, status_code=200):
    return templates.TemplateResponse(request, "integrations/list.html", {
        "rows": _rows(repo), "providers": PROVIDERS,
        "error": error, "form": form or {},
    }, status_code=status_code)

def _table_response(request, repo, *, status_code=200):
    return templates.TemplateResponse(request, "integrations/_table.html",
                                      {"rows": _rows(repo)}, status_code=status_code)

def _after_change(request, repo):
    """Swap the table for HTMX callers; plain form posts get a redirect."""
    if request.headers.get("HX-Request"):
        return _table_response(request, repo)
    return RedirectResponse("/integrations", status_code=303)

@router.get("", response_class=HTMLResponse)
def integrations_list(request: Request,
                      repo: SqliteIntegrationRepository = Depends(get_integration_repo)) -> HTMLResponse:
    """Render the integrations page."""
    return _list_response(request, repo)

@router.post("/connect", response_class=Response)
def connect_integration(request: Request,
                        provider: str = Form(...), external_id: str = Form(...),
                        repo: SqliteIntegrationRepository = Depends(get_integration_repo)) -> Response:
    """Connect a new integration."""
    try:
        integration = Integration(provider=provider, external_id=external_id)
        repo.connect(integration)
    except ValueError as e:
        return _list_response(request, repo, error=str(e),
                              form={"provider": provider, "external_id": external_id})
    return _after_change(request, repo)

@router.post("/{provider}/disconnect", response_class=Response)
def disconnect_integration(request: Request, provider: str,
                           repo: SqliteIntegrationRepository = Depends(get_integration_repo)) -> Response:
    """Disconnect an integration."""
    try:
        repo.delete(provider)
    except KeyError as e:
        raise not_found(str(e))
    return _after_change(request, repo)

@router.post("/{provider}/sync", response_class=Response)
def sync_integration(request: Request, provider: str,
                     repo: SqliteIntegrationRepository = Depends(get_integration_repo)) -> Response:
    """Sync an integration."""
    try:
        integration = repo.get(provider)
    except KeyError as e:
        raise not_found(str(e))
    integration.mark_synced(now_iso())
    repo.update(integration)
    return _after_change(request, repo)
