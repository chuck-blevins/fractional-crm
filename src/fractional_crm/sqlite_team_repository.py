import sqlite3
from typing import List, Optional
from fractional_crm.team import TeamMember

class SqliteTeamRepository:
    def __init__(self, path: str = ":memory:") -> None:
        """Initialize the SQLite database connection and cursor."""
        self.connection = sqlite3.connect(path)
        self._cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        """Create tables if they do not exist."""
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            );
        """)
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                name TEXT,
                email TEXT,
                role TEXT,
                UNIQUE(team_id, email)
            );
        """)
        self.connection.commit()

    def create_team(self, name: str) -> int:
        """Create a new team and return its ID."""
        self._cursor.execute("INSERT INTO teams(name) VALUES(?)", (name,))
        self.connection.commit()
        return self._cursor.lastrowid

    def list_teams(self) -> List[dict]:
        """List all teams."""
        rows = self._cursor.execute("SELECT id, name FROM teams").fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]

    def team_exists(self, team_id: int) -> bool:
        """Check if a team exists by ID."""
        row = self._cursor.execute("SELECT 1 FROM teams WHERE id=?", (team_id,)).fetchone()
        return row is not None

    def add_member(self, team_id: int, member: TeamMember) -> None:
        """Add a new member to a team."""
        if not self.team_exists(team_id):
            raise KeyError(f"No team {team_id}")
        try:
            self._cursor.execute(
                "INSERT INTO team_members(team_id, name, email, role) VALUES(?,?,?,?)",
                (team_id, member.name, member.email, member.role)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Member email already on team")

    def list_members(self, team_id: int, role: Optional[str] = None) -> List[TeamMember]:
        """List members of a team by role."""
        if role is None:
            rows = self._cursor.execute(
                "SELECT name, email, role FROM team_members WHERE team_id=? ORDER BY id",
                (team_id,)
            ).fetchall()
        else:
            rows = self._cursor.execute(
                "SELECT name, email, role FROM team_members WHERE team_id=? AND role=? ORDER BY id",
                (team_id, role)
            ).fetchall()
        return [TeamMember(name=r[0], email=r[1], role=r[2]) for r in rows]

    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()
