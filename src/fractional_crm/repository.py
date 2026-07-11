from typing import Dict, List
from fractional_crm.client import Client

class ClientRepository:
    """In-memory client repository."""

    def __init__(self) -> None:
        self._clients: Dict[str, Client] = {}

    def add(self, client: Client) -> None:
        """Add a client to the repository. Raises ValueError if duplicate email."""
        if client.email in self._clients:
            raise ValueError(f"Client with email {client.email} already exists")
        self._clients[client.email] = client

    def get(self, email: str) -> Client:
        """Get a client by email. Raises KeyError if missing."""
        return self._clients[email]

    def list(self) -> List[Client]:
        """List all clients."""
        return list(self._clients.values())

    def update(self, client: Client) -> None:
        """Update an existing client. Raises KeyError if missing."""
        if client.email not in self._clients:
            raise KeyError(f"Client with email {client.email} does not exist")
        self._clients[client.email] = client

    def delete(self, email: str) -> None:
        """Delete a client by email. Raises KeyError if missing."""
        if email not in self._clients:
            raise KeyError(f"Client with email {email} does not exist")
        del self._clients[email]
