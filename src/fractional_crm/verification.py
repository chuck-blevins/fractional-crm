import hmac
import secrets
from typing import Dict, Set

from fractional_crm.client import Client


class EmailVerification:
    """A per-Client email-verification state machine."""

    def __init__(self) -> None:
        self._pending_tokens: Dict[str, str] = {}
        self._verified_emails: Set[str] = set()

    def request(self, client: Client) -> str:
        """Generate a random token and store it as the pending token for client.email."""
        token = secrets.token_urlsafe()
        self._pending_tokens[client.email] = token
        return token

    def verify(self, client: Client, token: str) -> bool:
        """Verify the client's email using the provided token (constant-time compare)."""
        if client.email not in self._pending_tokens:
            raise KeyError("No pending token for this client")
        if not hmac.compare_digest(self._pending_tokens[client.email], token):
            raise ValueError("Invalid token")
        self._verified_emails.add(client.email)
        del self._pending_tokens[client.email]
        return True

    def is_verified(self, client: Client) -> bool:
        """Return True iff client.email has been verified."""
        return client.email in self._verified_emails

    def require_verified(self, client: Client) -> None:
        """Raise ValueError if client.email is not verified; otherwise do nothing."""
        if not self.is_verified(client):
            raise ValueError("Client email is not verified")
