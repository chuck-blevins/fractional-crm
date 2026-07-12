from typing import Dict
import secrets
import hashlib
from fractional_crm.client import Client

class PasscodeAuth:
    """A per-Client passcode authentication system."""

    def __init__(self) -> None:
        self._passcodes: Dict[str, tuple[bytes, str]] = {}

    def set_passcode(self, client: Client, passcode: str) -> None:
        """Set a passcode for the given client. Raises ValueError if passcode is invalid."""
        if not (passcode.isascii() and passcode.isdigit() and 4 <= len(passcode) <= 8):
            raise ValueError("Invalid passcode")
        salt = secrets.token_bytes(16)
        stored_passcode = hashlib.sha256(salt + passcode.encode()).hexdigest()
        self._passcodes[client.email] = (salt, stored_passcode)

    def has_passcode(self, client: Client) -> bool:
        """Check if the given client has a stored passcode."""
        return client.email in self._passcodes

    def authenticate(self, client: Client, passcode: str) -> bool:
        """Authenticate the given client with the provided passcode. Raises KeyError if no passcode is set."""
        if not self.has_passcode(client):
            raise KeyError("No passcode set for this client")
        salt, stored_passcode = self._passcodes[client.email]
        return hashlib.sha256(salt + passcode.encode()).hexdigest() == stored_passcode

    def clear_passcode(self, client: Client) -> None:
        """Remove the passcode for the given client. Raises KeyError if no passcode is set."""
        if not self.has_passcode(client):
            raise KeyError("No passcode set for this client")
        del self._passcodes[client.email]
