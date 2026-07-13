import hashlib
import hmac
import secrets
from typing import Dict, Tuple

from fractional_crm.client import Client

# Passcodes are low-entropy (4-8 digit PINs), so a fast hash would be brute-forced
# in milliseconds if the store leaked. Use a slow KDF and a constant-time compare.
_PBKDF2_ITERATIONS = 200_000


class PasscodeAuth:
    """A per-Client passcode authentication system.

    Stores only a random salt and a PBKDF2-HMAC-SHA256 derivation of the passcode
    (never the passcode itself), and verifies in constant time.
    """

    def __init__(self) -> None:
        self._passcodes: Dict[str, Tuple[bytes, bytes]] = {}

    @staticmethod
    def _derive(passcode: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", passcode.encode(), salt, _PBKDF2_ITERATIONS)

    def set_passcode(self, client: Client, passcode: str) -> None:
        """Set a passcode for the client. Raises ValueError if it is not a 4-8 digit PIN."""
        if not (passcode.isascii() and passcode.isdigit() and 4 <= len(passcode) <= 8):
            raise ValueError("Invalid passcode")
        salt = secrets.token_bytes(16)
        self._passcodes[client.email] = (salt, self._derive(passcode, salt))

    def has_passcode(self, client: Client) -> bool:
        """Return True iff the client has a stored passcode."""
        return client.email in self._passcodes

    def authenticate(self, client: Client, passcode: str) -> bool:
        """Return True iff the passcode matches. Raises KeyError if none is set."""
        if not self.has_passcode(client):
            raise KeyError("No passcode set for this client")
        salt, stored = self._passcodes[client.email]
        return hmac.compare_digest(self._derive(passcode, salt), stored)

    def clear_passcode(self, client: Client) -> None:
        """Remove the client's passcode. Raises KeyError if none is set."""
        if not self.has_passcode(client):
            raise KeyError("No passcode set for this client")
        del self._passcodes[client.email]
