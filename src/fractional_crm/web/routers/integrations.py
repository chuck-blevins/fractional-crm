from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from fractional_crm.integration import Integration
from fractional_crm.sqlite_integration_repository import SqliteIntegrationRepository
from fractional_crm.web.deps import get_integration_repo
from fractional_crm.web.errors import conflict, invalid, not_found

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

class IntegrationIn(BaseModel): provider: str; external_id: str
class SyncIn(BaseModel): timestamp: str
class IntegrationOut(BaseModel): provider: str; external_id: str; status: str; last_synced_at: str | None = None

def _to_out(i: Integration) -> IntegrationOut:
    return IntegrationOut(provider=i.provider, external_id=i.external_id, status=i.status, last_synced_at=i.last_synced_at)

@router.get("")
def list_integrations(repo: SqliteIntegrationRepository = Depends(get_integration_repo)) -> list[IntegrationOut]:
    """List all integrations."""
    return [_to_out(i) for i in repo.list()]

@router.post("", status_code=201)
def connect_integration(payload: IntegrationIn, repo: SqliteIntegrationRepository = Depends(get_integration_repo)) -> IntegrationOut:
    """Connect a new integration."""
    try:
        i = Integration(provider=payload.provider, external_id=payload.external_id)
    except ValueError as e:
        raise invalid(str(e))
    try:
        repo.connect(i)
    except ValueError as e:
        raise conflict(str(e))
    return _to_out(i)

@router.delete("/{provider}", status_code=204)
def disconnect_integration(provider: str, repo: SqliteIntegrationRepository = Depends(get_integration_repo)) -> Response:
    """Disconnect an integration."""
    try:
        repo.delete(provider)
    except KeyError as e:
        raise not_found(str(e))
    return Response(status_code=204)

@router.post("/{provider}/sync")
def sync_integration(provider: str, payload: SyncIn, repo: SqliteIntegrationRepository = Depends(get_integration_repo)) -> IntegrationOut:
    """Sync an integration."""
    try:
        i = repo.get(provider)
    except KeyError as e:
        raise not_found(str(e))
    try:
        i.mark_synced(payload.timestamp)
    except ValueError as e:
        raise invalid(str(e))
    repo.update(i)
    return _to_out(i)
