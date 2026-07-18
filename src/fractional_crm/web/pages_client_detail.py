"""Client detail page: profile, interactions timeline, and log-interaction form."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fractional_crm.interaction import KINDS, Interaction
from fractional_crm.sqlite_repository import SqliteClientRepository
from fractional_crm.sqlite_interaction_repository import SqliteInteractionRepository
from fractional_crm.web.deps import get_client_repo, get_interaction_repo
from fractional_crm.web.errors import not_found
from fractional_crm.web.templates import templates

router = APIRouter(prefix="/clients")

def _timeline_response(request, interactions, *, template="clients/_timeline.html", status_code=200):
    return templates.TemplateResponse(request, template, {"interactions": interactions}, status_code=status_code)

def _detail_response(request, client, interactions, *, error=None, form=None, status_code=200):
    return templates.TemplateResponse(request, "clients/detail.html", {
        "client": client, "interactions": interactions, "kinds": KINDS,
        "error": error, "form": form or {},
    }, status_code=status_code)

@router.get("/{email}", response_class=HTMLResponse)
def client_detail(request: Request, email: str,
                  clients: SqliteClientRepository = Depends(get_client_repo),
                  inter_repo: SqliteInteractionRepository = Depends(get_interaction_repo)) -> HTMLResponse:
    """Render the detail page for a client."""
    try:
        client = clients.get(email)
    except KeyError as e:
        raise not_found(str(e))
    interactions = inter_repo.list_for_client(email)
    return _detail_response(request, client, interactions)

@router.post("/{email}/interactions", response_class=Response)
def log_interaction(request: Request, email: str,
                    date: str = Form(...), kind: str = Form(...), summary: str = Form(""),
                    clients: SqliteClientRepository = Depends(get_client_repo),
                    inter_repo: SqliteInteractionRepository = Depends(get_interaction_repo)) -> Response:
    """Log a new interaction for a client."""
    try:
        client = clients.get(email)
    except KeyError as e:
        raise not_found(str(e))
    try:
        interaction = Interaction(client_email=email, date=date, kind=kind, summary=summary)
        inter_repo.add(interaction)
    except ValueError as e:
        client = clients.get(email)
        interactions = inter_repo.list_for_client(email)
        return _detail_response(request, client, interactions, error=str(e),
                               form={"date": date, "kind": kind, "summary": summary})
    interactions = inter_repo.list_for_client(email)
    if request.headers.get("HX-Request"):
        return _timeline_response(request, interactions)
    return RedirectResponse(f"/clients/{email}", status_code=303)
