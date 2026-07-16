import sqlite3
from typing import List
from fractional_crm.interaction import Interaction

class SqliteInteractionRepository:
    """SQLite repository for storing and retrieving interactions."""

    def __init__(self, path: str = ":memory:") -> None:
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self) -> None:
        """Create the interactions table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_email TEXT,
                date TEXT,
                kind TEXT,
                summary TEXT
            )
        """)
        self.connection.commit()

    def add(self, interaction: Interaction) -> None:
        """Add an interaction to the repository."""
        self.cursor.execute("""
            INSERT INTO interactions (client_email, date, kind, summary)
            VALUES (?, ?, ?, ?)
        """, (interaction.client_email, interaction.date, interaction.kind, interaction.summary))
        self.connection.commit()

    def list_for_client(self, client_email: str) -> List[Interaction]:
        """List all interactions for a specific client."""
        self.cursor.execute("""
            SELECT client_email, date, kind, summary
            FROM interactions
            WHERE client_email=?
            ORDER BY date DESC, id DESC
        """, (client_email,))
        rows = self.cursor.fetchall()
        return [Interaction(client_email=r[0], date=r[1], kind=r[2], summary=r[3]) for r in rows]

    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()
