from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from fractional_crm.engagement import Engagement
from fractional_crm.sqlite_repository import SqliteEngagementRepository
from fractional_crm.web.deps import get_engagement_repo
from fractional_crm.web.errors import conflict, invalid, not_found

router = APIRouter(prefix="/api/engagements", tags=["engagements"])

class EngagementIn(BaseModel):
    client_email: str
    role: str
    monthly_rate: float
    start_date: str
    status: str
    end_date: str | None = None

class EngagementOut(EngagementIn):
    pass

def _to_out(e: Engagement) -> EngagementOut:
    """Convert an Engagement object to an EngagementOut object."""
    return EngagementOut(
        client_email=e.client_email,
        role=e.role,
        monthly_rate=e.monthly_rate,
        start_date=e.start_date,
        status=e.status,
        end_date=e.end_date
    )

@router.get("")
def list_engagements(client_email: str | None = None, repo: SqliteEngagementRepository = Depends(get_engagement_repo)) -> list[EngagementOut]:
    """List engagements, optionally filtering by client email."""
    if client_email:
        return [_to_out(e) for e in repo.list() if e.client_email == client_email]
    else:
        return [_to_out(e) for e in repo.list()]

@router.post("", status_code=201)
def create_engagement(payload: EngagementIn, repo: SqliteEngagementRepository = Depends(get_engagement_repo)) -> EngagementOut:
    """Create a new engagement."""
    try:
        e = Engagement(**payload.model_dump())
    except ValueError as e:
        raise invalid(str(e))
    try:
        repo.add(e)
    except ValueError as e:
        raise conflict(str(e))
    return _to_out(e)

@router.get("/{client_email}")
def get_engagement(client_email: str, repo: SqliteEngagementRepository = Depends(get_engagement_repo)) -> EngagementOut:
    """Get an engagement by client email."""
    try:
        return _to_out(repo.get(client_email))
    except KeyError as e:
        raise not_found(str(e))

@router.put("/{client_email}")
def update_engagement(client_email: str, payload: EngagementIn, repo: SqliteEngagementRepository = Depends(get_engagement_repo)) -> EngagementOut:
    """Update an engagement by client email."""
    try:
        e = Engagement(**payload.model_dump())
    except ValueError as e:
        raise invalid(str(e))
    try:
        repo.update(e)
    except KeyError as e:
        raise not_found(str(e))
    return _to_out(e)

@router.delete("/{client_email}", status_code=204)
def delete_engagement(client_email: str, repo: SqliteEngagementRepository = Depends(get_engagement_repo)) -> Response:
    """Delete an engagement by client email."""
    try:
        repo.delete(client_email)
    except KeyError as e:
        raise not_found(str(e))
    return Response(status_code=204)
