import re

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
_ALLOWED_STATUSES = ("prospect", "active", "paused", "closed")
_ALLOWED_ENGAGEMENT_TYPES = ("coo", "cpo", "advisor")


class Client:
    """A CRM client for a fractional COO/CPO engagement."""

    def __init__(self, name: str, company: str, email: str,
                 status: str, engagement_type: str) -> None:
        self.name = self._validate_name(name)
        self.company = company
        self.email = self._validate_email(email)
        self.status = self._validate_status(status)
        self.engagement_type = self._validate_engagement_type(engagement_type)

    @staticmethod
    def _validate_name(name: str) -> str:
        """Return the stripped name; raise ValueError if empty."""
        name = name.strip()
        if not name:
            raise ValueError("name cannot be empty")
        return name

    @staticmethod
    def _validate_email(email: str) -> str:
        """Return email if it is a valid address; else raise ValueError."""
        if not _EMAIL_RE.match(email):
            raise ValueError(f"invalid email address: {email!r}")
        return email

    @staticmethod
    def _validate_status(status: str) -> str:
        """Return status if it is an allowed value; else raise ValueError."""
        if status not in _ALLOWED_STATUSES:
            raise ValueError(f"invalid status: {status!r}")
        return status

    @staticmethod
    def _validate_engagement_type(engagement_type: str) -> str:
        """Return engagement_type if it is an allowed value; else raise ValueError."""
        if engagement_type not in _ALLOWED_ENGAGEMENT_TYPES:
            raise ValueError(f"invalid engagement type: {engagement_type!r}")
        return engagement_type
