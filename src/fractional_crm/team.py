from typing import Dict, List
import re

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
#: Allowed team-member roles. Public so the web layer drives its <select> from the
#: domain instead of re-encoding the list in a template (CRB-33, as CRB-30/31 did).
ROLES = ("admin", "member", "guest")
_ALLOWED_ROLES = ROLES  # retained so existing private references keep working


class TeamMember:
    """A team member with a name, email, and role."""

    def __init__(self, name: str, email: str, role: str) -> None:
        self.name = self._validate_name(name)
        self.email = self._validate_email(email)
        self.role = self._validate_role(role)

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
    def _validate_role(role: str) -> str:
        """Return role if it is an allowed value; else raise ValueError."""
        if role not in _ALLOWED_ROLES:
            raise ValueError(f"invalid role: {role!r}")
        return role


class Team:
    """A team managing members keyed by email."""

    def __init__(self, name: str) -> None:
        self.name = self._validate_name(name)
        self.members: Dict[str, TeamMember] = {}

    @staticmethod
    def _validate_name(name: str) -> str:
        """Return the stripped name; raise ValueError if empty."""
        name = name.strip()
        if not name:
            raise ValueError("name cannot be empty")
        return name

    @staticmethod
    def _validate_role(role: str) -> str:
        """Return role if it is an allowed value; else raise ValueError."""
        if role not in _ALLOWED_ROLES:
            raise ValueError(f"invalid role: {role!r}")
        return role

    def add_member(self, member: TeamMember) -> None:
        """Add a member to the team. Raises ValueError if duplicate email."""
        if member.email in self.members:
            raise ValueError(f"Team already has a member with email {member.email}")
        self.members[member.email] = member

    def get_member(self, email: str) -> TeamMember:
        """Get a member by email. Raises KeyError if missing."""
        return self.members[email]

    def remove_member(self, email: str) -> None:
        """Remove a member by email. Raises KeyError if missing."""
        if email not in self.members:
            raise KeyError(f"Team has no member with email {email}")
        del self.members[email]

    def list_members(self) -> List[TeamMember]:
        """List all members in insertion order."""
        return list(self.members.values())

    def members_with_role(self, role: str) -> List[TeamMember]:
        """Return members with the given role in insertion order. Raises ValueError if invalid role."""
        self._validate_role(role)
        return [member for member in self.members.values() if member.role == role]
