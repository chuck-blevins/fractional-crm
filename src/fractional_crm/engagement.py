import datetime

class Engagement:
    """An engagement model with validation."""

    def __init__(self, client_email: str, role: str, monthly_rate: float,
                 start_date: str, status: str, end_date: str = None) -> None:
        self.client_email = self._validate_client_email(client_email)
        self.role = self._validate_role(role)
        self.monthly_rate = self._validate_monthly_rate(monthly_rate)
        self.start_date = self._validate_start_date(start_date)
        self.end_date = self._validate_end_date(end_date, start_date)
        self.status = self._validate_status(status)

    @staticmethod
    def _validate_client_email(email: str) -> str:
        """Return email if it is a valid address; else raise ValueError."""
        return email.strip()

    @staticmethod
    def _validate_role(role: str) -> str:
        """Return role if it is an allowed value; else raise ValueError."""
        allowed_roles = ["coo", "cpo", "advisor"]
        if role not in allowed_roles:
            raise ValueError(f"invalid role: {role!r}")
        return role

    @staticmethod
    def _validate_monthly_rate(monthly_rate: float) -> float:
        """Return monthly_rate if it is positive; else raise ValueError."""
        if monthly_rate <= 0:
            raise ValueError("monthly rate must be greater than 0")
        return monthly_rate

    @staticmethod
    def _validate_start_date(start_date: str) -> datetime.date:
        """Return start_date as a date object; else raise ValueError."""
        try:
            return datetime.date.fromisoformat(start_date)
        except ValueError:
            raise ValueError(f"invalid start date: {start_date!r}")

    @staticmethod
    def _validate_end_date(end_date: str, start_date: str) -> datetime.date:
        """Return end_date as a date object if valid; else raise ValueError."""
        if end_date is None:
            return None
        try:
            end_date = datetime.date.fromisoformat(end_date)
        except ValueError:
            raise ValueError(f"invalid end date: {end_date!r}")
        if end_date < datetime.date.fromisoformat(start_date):
            raise ValueError("end date must be on or after start date")
        return end_date

    @staticmethod
    def _validate_status(status: str) -> str:
        """Return status if it is an allowed value; else raise ValueError."""
        allowed_statuses = ["proposed", "active", "completed", "cancelled"]
        if status not in allowed_statuses:
            raise ValueError(f"invalid status: {status!r}")
        return status
