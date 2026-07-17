from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from fractional_crm.csv_io import export_clients_csv
from fractional_crm.importer import ClientImporter
from fractional_crm.sqlite_repository import SqliteClientRepository
from fractional_crm.web.deps import get_client_repo

router = APIRouter(prefix="/api/clients/csv", tags=["csv"])
MAX_BYTES = 5 * 1024 * 1024

@router.get("/export")
def export_clients(repo: SqliteClientRepository = Depends(get_client_repo)) -> Response:
    """Export clients to CSV."""
    text = export_clients_csv(repo)
    return Response(content=text, media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="clients.csv"'})

@router.post("/import")
def import_clients(file: UploadFile = File(...), repo: SqliteClientRepository = Depends(get_client_repo)) -> dict:
    """Import clients from CSV or JSON file."""
    content = file.file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="file too large")
    text = content.decode("utf-8")
    importer = ClientImporter(repo)
    filename = file.filename or ""
    try:
        if filename.endswith(".json"):
            result = importer.import_json(text)
        else:
            result = importer.import_csv(text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"imported": len(result.imported), "errors": result.errors}
