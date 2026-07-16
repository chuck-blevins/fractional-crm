"""Clients JSON API: CRUD plus status transitions over the domain Client."""
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from fractional_crm.client import Client
from fractional_crm.sqlite_repository import SqliteClientRepository
from fractional_crm.web.deps import get_client_repo
from fractional_crm.web.errors import conflict, invalid, not_found

router = APIRouter(prefix="/api/clients", tags=["clients"])


class ClientIn(BaseModel):
    """Request body for creating or updating a client."""

    name: str
    company: str
    email: str
    status: str
    engagement_type: str


class ClientOut(ClientIn):
    """Response body for a client."""


class StatusIn(BaseModel):
    """Request body for a status transition."""

    status: str


def _to_out(c: Client) -> ClientOut:
    """Convert a domain Client into a ClientOut response model."""
    return ClientOut(
        name=c.name,
        company=c.company,
        email=c.email,
        status=c.status,
        engagement_type=c.engagement_type,
    )


@router.get("")
def list_clients(repo: SqliteClientRepository = Depends(get_client_repo)) -> list[ClientOut]:
    """Return all clients."""
    return [_to_out(c) for c in repo.list()]


@router.post("", status_code=201)
def create_client(
    payload: ClientIn, repo: SqliteClientRepository = Depends(get_client_repo)
) -> ClientOut:
    """Create a client; 422 on invalid fields, 409 on a duplicate email."""
    try:
        c = Client(**payload.model_dump())
    except ValueError as e:
        raise invalid(str(e))
    try:
        repo.add(c)
    except ValueError as e:
        raise conflict(str(e))
    return _to_out(c)


@router.get("/{email}")
def get_client(
    email: str, repo: SqliteClientRepository = Depends(get_client_repo)
) -> ClientOut:
    """Return one client by email; 404 if missing."""
    try:
        return _to_out(repo.get(email))
    except KeyError as e:
        raise not_found(str(e))


@router.put("/{email}")
def update_client(
    email: str, payload: ClientIn, repo: SqliteClientRepository = Depends(get_client_repo)
) -> ClientOut:
    """Update a client; 422 on invalid fields, 404 if missing."""
    try:
        c = Client(**payload.model_dump())
    except ValueError as e:
        raise invalid(str(e))
    try:
        repo.update(c)
    except KeyError as e:
        raise not_found(str(e))
    return _to_out(c)


@router.delete("/{email}", status_code=204)
def delete_client(
    email: str, repo: SqliteClientRepository = Depends(get_client_repo)
) -> Response:
    """Delete a client; 404 if missing."""
    try:
        repo.delete(email)
    except KeyError as e:
        raise not_found(str(e))
    return Response(status_code=204)


@router.post("/{email}/status")
def transition_status(
    email: str, body: StatusIn, repo: SqliteClientRepository = Depends(get_client_repo)
) -> ClientOut:
    """Transition a client's status; 404 if missing, 422 if the transition is disallowed."""
    try:
        c = repo.get(email)
    except KeyError as e:
        raise not_found(str(e))
    try:
        c.transition_to(body.status)
    except ValueError as e:
        raise invalid(str(e))
    repo.update(c)
    return _to_out(c)
