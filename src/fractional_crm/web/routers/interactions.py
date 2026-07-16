from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fractional_crm.interaction import Interaction
from fractional_crm.sqlite_repository import SqliteClientRepository
from fractional_crm.sqlite_interaction_repository import SqliteInteractionRepository
from fractional_crm.web.deps import get_client_repo, get_interaction_repo
from fractional_crm.web.errors import invalid, not_found

router = APIRouter(prefix="/api/clients", tags=["interactions"])

class InteractionIn(BaseModel):
    """Request model for creating an interaction."""
    date: str
    kind: str
    summary: str

class InteractionOut(InteractionIn):
    """Response model for interactions."""
    client_email: str

def _to_out(i: Interaction) -> InteractionOut:
    """Converts an Interaction to InteractionOut."""
    return InteractionOut(client_email=i.client_email, date=i.date, kind=i.kind, summary=i.summary)

@router.post("/{email}/interactions", status_code=201)
def create_interaction(email: str, payload: InteractionIn, clients: SqliteClientRepository = Depends(get_client_repo), repo: SqliteInteractionRepository = Depends(get_interaction_repo)) -> InteractionOut:
    """Creates a new interaction for the given client email."""
    try:
        clients.get(email)
    except KeyError as e:
        raise not_found(str(e))
    try:
        i = Interaction(client_email=email, date=payload.date, kind=payload.kind, summary=payload.summary)
    except ValueError as e:
        raise invalid(str(e))
    repo.add(i)
    return _to_out(i)

@router.get("/{email}/interactions")
def list_interactions(email: str, repo: SqliteInteractionRepository = Depends(get_interaction_repo)) -> list[InteractionOut]:
    """Lists all interactions for the given client email."""
    return [_to_out(i) for i in repo.list_for_client(email)]
