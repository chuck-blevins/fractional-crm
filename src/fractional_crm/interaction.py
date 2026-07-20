import datetime
import re

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")

#: Allowed interaction kinds. Public so the web layer drives its <select> from the domain (CRB-32).
KINDS = ("call", "email", "meeting", "note")

class Interaction:
    """An interaction with a client. Dates are kept as ISO strings."""

    def __init__(self, client_email: str, date: str, kind: str, summary: str) -> None:
        self.client_email = self._validate_email(client_email)
        self.date = self._validate_date(date)
        self.kind = self._validate_kind(kind)
        self.summary = self._validate_summary(summary)

    @staticmethod
    def _validate_email(email: str) -> str:
        """Return email if it is a valid address; else raise ValueError."""
        if not _EMAIL_RE.match(email):
            raise ValueError(f"invalid client_email: {email!r}")
        return email

    @staticmethod
    def _validate_date(value: str) -> str:
        """Return the original ISO date string if it parses; else raise ValueError."""
        try:
            datetime.date.fromisoformat(value)
        except (ValueError, TypeError):
            raise ValueError(f"invalid date: {value!r}")
        return value

    @staticmethod
    def _validate_kind(kind: str) -> str:
        """Return kind if it is an allowed value; else raise ValueError."""
        if kind not in KINDS:
            raise ValueError(f"invalid kind: {kind!r}")
        return kind

    @staticmethod
    def _validate_summary(summary: str) -> str:
        """Return stripped summary if it is non-empty; else raise ValueError."""
        stripped = summary.strip()
        if not stripped:
            raise ValueError("summary must be non-empty")
        return stripped
