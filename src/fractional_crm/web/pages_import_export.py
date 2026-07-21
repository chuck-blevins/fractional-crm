"""Import/Export page: CSV export link + client import form."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fractional_crm.web.templates import templates

router = APIRouter(prefix="/import-export")

@router.get("", response_class=HTMLResponse)
def import_export(request: Request) -> HTMLResponse:
    """Render the import/export page (CSV export link + client import form)."""
    return templates.TemplateResponse(request, "import_export/index.html", {})
