"""Clients UI: accessible server-rendered list, create/edit forms, and status transitions.

Reuses the domain Client + repository. HTMX enhances create/status without full reloads,
but every action also works as a plain form POST -> redirect (progressive enhancement).
Handlers are sync `def` to stay on the sqlite repo's thread (see .agent/lessons.md).
"""
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from fractional_crm.client import ALLOWED_TRANSITIONS, ENGAGEMENT_TYPES, STATUSES, Client
from fractional_crm.sqlite_repository import SqliteClientRepository
from fractional_crm.web.deps import get_client_repo
from fractional_crm.web.errors import not_found
from fractional_crm.web.templates import templates
from fractional_crm.importer import ClientImporter

router = APIRouter(prefix="/clients")
MAX_IMPORT_BYTES = 5 * 1024 * 1024

def _rows(repo: SqliteClientRepository) -> list[dict]:
    """Return [{client, transitions}] for every stored client (transitions = allowed next statuses)."""
    return [{"client": c, "transitions": ALLOWED_TRANSITIONS.get(c.status, [])} for c in repo.list()]


def _list_response(request: Request, repo: SqliteClientRepository, *, template: str = "clients/list.html",
                   status_code: int = 200, import_result: dict | None = None) -> HTMLResponse:
    """Render the clients list (full page) or the `_table.html` fragment for HTMX swaps."""
    return templates.TemplateResponse(request, template,
                                      {"rows": _rows(repo), "import_result": import_result},
                                      status_code=status_code)


def _form_response(request: Request, *, mode: str, action: str, form: dict, error: str | None,
                   email_readonly: bool, status_code: int = 200) -> HTMLResponse:
    """Render the create/edit client form (optionally with an error summary)."""
    return templates.TemplateResponse(request, "clients/form.html", {
        "mode": mode, "action": action, "form": form, "error": error,
        "statuses": STATUSES, "engagement_types": ENGAGEMENT_TYPES, "email_readonly": email_readonly,
    }, status_code=status_code)


@router.get("", response_class=HTMLResponse)
def list_clients(request: Request, repo: SqliteClientRepository = Depends(get_client_repo)) -> HTMLResponse:
    """Render the clients table with per-row status controls."""
    return _list_response(request, repo)


@router.get("/new", response_class=HTMLResponse)
def new_client_form(request: Request) -> HTMLResponse:
    """Render the empty create-client form."""
    return _form_response(request, mode="create", action="/clients", form={}, error=None, email_readonly=False)


@router.post("")
def create_client(
    request: Request,
    name: str = Form(""), company: str = Form(""), email: str = Form(""),
    status: str = Form("prospect"), engagement_type: str = Form("coo"),
    repo: SqliteClientRepository = Depends(get_client_repo),
) -> Response:
    """Create a client; re-render the form with an error (200) on invalid/duplicate, else redirect to /clients."""
    fields = {"name": name, "company": company, "email": email, "status": status, "engagement_type": engagement_type}
    try:
        repo.add(Client(**fields))
    except ValueError as e:
        return _form_response(request, mode="create", action="/clients", form=fields, error=str(e), email_readonly=False)
    if request.headers.get("HX-Request"):
        return _list_response(request, repo, template="clients/_table.html")
    return RedirectResponse("/clients", status_code=303)


@router.post("/import", response_class=HTMLResponse)
def import_clients_from_upload(request: Request, file: UploadFile = File(...),
                              repo: SqliteClientRepository = Depends(get_client_repo)) -> HTMLResponse:
    """Import clients from an uploaded CSV/JSON file; re-render the list with a summary.

    Every failure mode (too large, non-UTF-8, unparseable) renders the page with an
    error instead of a 500, so the plain form POST always returns readable HTML.
    """
    content = file.file.read()
    if len(content) > MAX_IMPORT_BYTES:
        return _list_response(request, repo, status_code=413,
                              import_result={"imported": 0, "errors": [{"row": 0, "error": "file too large"}]})
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return _list_response(request, repo, status_code=400,
                              import_result={"imported": 0, "errors": [{"row": 0, "error": "file is not valid UTF-8"}]})
    importer = ClientImporter(repo)
    filename = file.filename or ""
    try:
        if filename.endswith(".json"):
            result = importer.import_json(text)
        else:
            result = importer.import_csv(text)
    except ValueError as exc:
        return _list_response(request, repo, status_code=400,
                              import_result={"imported": 0, "errors": [{"row": 0, "error": str(exc)}]})
    return _list_response(request, repo,
                          import_result={"imported": len(result.imported), "errors": result.errors})

@router.get("/{email}/edit", response_class=HTMLResponse)
def edit_client_form(request: Request, email: str,
                     repo: SqliteClientRepository = Depends(get_client_repo)) -> HTMLResponse:
    """Render the edit form for one client; 404 if missing."""
    try:
        c = repo.get(email)
    except KeyError as e:
        raise not_found(str(e))
    fields = {"name": c.name, "company": c.company, "email": c.email,
              "status": c.status, "engagement_type": c.engagement_type}
    return _form_response(request, mode="edit", action=f"/clients/{email}", form=fields, error=None, email_readonly=True)


@router.post("/{email}")
def update_client(
    request: Request, email: str,
    name: str = Form(""), company: str = Form(""),
    status: str = Form("prospect"), engagement_type: str = Form("coo"),
    repo: SqliteClientRepository = Depends(get_client_repo),
) -> Response:
    """Update a client (email is the immutable key); re-render on error, else redirect to /clients."""
    fields = {"name": name, "company": company, "email": email, "status": status, "engagement_type": engagement_type}
    try:
        repo.update(Client(**fields))
    except ValueError as e:
        return _form_response(request, mode="edit", action=f"/clients/{email}", form=fields, error=str(e), email_readonly=True)
    except KeyError as e:
        raise not_found(str(e))
    if request.headers.get("HX-Request"):
        return _list_response(request, repo, template="clients/_table.html")
    return RedirectResponse("/clients", status_code=303)


@router.post("/{email}/status")
def transition_client(
    request: Request, email: str, status: str = Form(...),
    repo: SqliteClientRepository = Depends(get_client_repo),
) -> Response:
    """Apply an allowed status transition; on an invalid transition re-render the list unchanged."""
    try:
        c = repo.get(email)
    except KeyError as e:
        raise not_found(str(e))
    try:
        c.transition_to(status)
        repo.update(c)
    except ValueError:
        return _list_response(request, repo)  # invalid transition: list unchanged
    if request.headers.get("HX-Request"):
        return _list_response(request, repo, template="clients/_table.html")
    return RedirectResponse("/clients", status_code=303)
