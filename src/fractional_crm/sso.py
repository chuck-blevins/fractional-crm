import base64
import binascii
import hashlib
import hmac
import json

from fractional_crm.client import Client


class GmailSSO:
    """Link Gmail clients to Google subject ids and verify signed SSO assertions.

    Assertion tokens are `base64url(json_body).base64url(HMAC-SHA256(secret, json_body))`,
    mirroring an IdP-issued, signature-verified assertion.
    """

    def __init__(self, secret: str) -> None:
        if not secret:
            raise ValueError("secret must be non-empty")
        self._secret = secret.encode()
        self._by_email: dict[str, str] = {}
        self._linked_ids: set[str] = set()

    def _sign(self, body: bytes) -> str:
        return base64.urlsafe_b64encode(
            hmac.new(self._secret, body, hashlib.sha256).digest()).decode()

    def link(self, client: Client, google_id: str) -> None:
        if not client.email.lower().endswith("@gmail.com"):
            raise ValueError("SSO linking requires a gmail.com address")
        if not google_id:
            raise ValueError("google_id must be non-empty")
        if google_id in self._linked_ids and self._by_email.get(client.email) != google_id:
            raise ValueError("google_id is already linked to another client")
        self._by_email[client.email] = google_id
        self._linked_ids.add(google_id)

    def is_linked(self, client: Client) -> bool:
        return client.email in self._by_email

    def unlink(self, client: Client) -> None:
        if client.email not in self._by_email:
            raise KeyError("client is not linked")
        self._linked_ids.discard(self._by_email.pop(client.email))

    def create_token(self, google_id: str, email: str) -> str:
        body = json.dumps({"google_id": google_id, "email": email}, sort_keys=True).encode()
        return f"{base64.urlsafe_b64encode(body).decode()}.{self._sign(body)}"

    def authenticate(self, client: Client, token: str) -> bool:
        if client.email not in self._by_email:
            raise KeyError("client is not linked")
        try:
            body_b64, sig = token.split(".")
            body = base64.urlsafe_b64decode(body_b64.encode())
            claims = json.loads(body)
        except (ValueError, binascii.Error):
            raise ValueError("malformed token")
        # constant-time signature check before trusting any claim
        if not hmac.compare_digest(self._sign(body), sig):
            raise ValueError("invalid token signature")
        return (claims.get("google_id") == self._by_email[client.email]
                and claims.get("email") == client.email)
