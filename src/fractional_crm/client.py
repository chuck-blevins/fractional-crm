class Client:
    allowed_statuses = ["prospect", "active", "paused", "closed"]
    allowed_engagement_types = ["coo", "cpo", "advisor"]

    def __init__(self, name: str, company: str, email: str, status: str, engagement_type: str):
        self.name = self._validate_name(name)
        self.company = company
        self.email = self._validate_email(email)
        self.status = self._validate_status(status)
        self.engagement_type = self._validate_engagement_type(engagement_type)

    @staticmethod
    def _validate_name(name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty")
        return name

    @staticmethod
    def _validate_email(email: str) -> str:
        local_part, domain = email.split("@")
        if not local_part or not domain or " " in email or "." not in domain or len(domain.split(".")[-1]) < 2:
            raise ValueError(f"Invalid email address: {email}")
        return email

    @staticmethod
    def _validate_status(status: str) -> str:
        if status not in Client.allowed_statuses:
            raise ValueError(f"Invalid status: {status}")
        return status

    @staticmethod
    def _validate_engagement_type(engagement_type: str) -> str:
        if engagement_type not in Client.allowed_engagement_types:
            raise ValueError(f"Invalid engagement type: {engagement_type}")
        return engagement_type
