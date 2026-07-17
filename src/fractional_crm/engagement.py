import datetime
import re

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
_ALLOWED_ROLES = ("coo", "cpo", "advisor")
_ALLOWED_STATUSES = ("proposed", "active", "completed", "cancelled")

#: Public aliases so the web layer drives its <select>s from the domain (CRB-31, pure refactor).
ROLES = _ALLOWED_ROLES
STATUSES = _ALLOWED_STATUSES


class Engagement:
    """A fractional engagement with a client. Dates are kept as ISO strings."""

    def __init__(self, client_email: str, role: str, monthly_rate: float,
                 start_date: str, status: str, end_date: str | None = None) -> None:
        self.client_email = self._validate_email(client_email)
        self.role = self._validate_role(role)
        self.monthly_rate = self._validate_monthly_rate(monthly_rate)
        self.start_date = self._validate_date(start_date, "start_date")
        self.end_date = self._validate_end_date(end_date, start_date)
        self.status = self._validate_status(status)

    @staticmethod
    def _validate_email(email: str) -> str:
        """Return email if it is a valid address; else raise ValueError."""
        if not _EMAIL_RE.match(email):
            raise ValueError(f"invalid client_email: {email!r}")
        return email

    @staticmethod
    def _validate_role(role: str) -> str:
        """Return role if it is an allowed value; else raise ValueError."""
        if role not in _ALLOWED_ROLES:
            raise ValueError(f"invalid role: {role!r}")
        return role

    @staticmethod
    def _validate_monthly_rate(rate: float) -> float:
        """Return rate if it is a positive number; else raise ValueError."""
        if rate <= 0:
            raise ValueError(f"monthly_rate must be positive: {rate!r}")
        return rate

    @staticmethod
    def _validate_date(value: str, field: str) -> str:
        """Return the original ISO date string if it parses; else raise ValueError."""
        try:
            datetime.date.fromisoformat(value)
        except (ValueError, TypeError):
            raise ValueError(f"invalid {field}: {value!r}")
        return value

    @classmethod
    def _validate_end_date(cls, end_date: str | None, start_date: str) -> str | None:
        """Return the end_date string (or None). Must parse and be >= start_date."""
        if end_date is None:
            return None
        cls._validate_date(end_date, "end_date")
        if datetime.date.fromisoformat(end_date) < datetime.date.fromisoformat(start_date):
            raise ValueError("end_date must be on or after start_date")
        return end_date

    @staticmethod
    def _validate_status(status: str) -> str:
        """Return status if it is an allowed value; else raise ValueError."""
        if status not in _ALLOWED_STATUSES:
            raise ValueError(f"invalid status: {status!r}")
        return status
