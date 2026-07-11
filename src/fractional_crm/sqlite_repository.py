import sqlite3
from typing import Dict, List
from fractional_crm.client import Client
from fractional_crm.engagement import Engagement


class SqliteClientRepository:
    """SQLite-backed client repository."""

    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path)
        self._cursor = self._conn.cursor()
        self._create_table()

    def _create_table(self) -> None:
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                email TEXT PRIMARY KEY,
                name TEXT,
                company TEXT,
                status TEXT,
                engagement_type TEXT
            )
        ''')
        self._conn.commit()

    def add(self, client: Client) -> None:
        """Add a client to the repository. Raises ValueError if duplicate email."""
        try:
            self._cursor.execute('''
                INSERT INTO clients (email, name, company, status, engagement_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (client.email, client.name, client.company, client.status, client.engagement_type))
            self._conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Client with email {client.email} already exists")

    def get(self, email: str) -> Client:
        """Get a client by email. Raises KeyError if missing."""
        self._cursor.execute('SELECT * FROM clients WHERE email = ?', (email,))
        row = self._cursor.fetchone()
        if row is None:
            raise KeyError(f"Client with email {email} does not exist")
        return Client(name=row[1], company=row[2], email=row[0], status=row[3], engagement_type=row[4])

    def list(self) -> List[Client]:
        """List all clients."""
        self._cursor.execute('SELECT * FROM clients')
        rows = self._cursor.fetchall()
        return [Client(name=row[1], company=row[2], email=row[0], status=row[3], engagement_type=row[4]) for row in rows]

    def update(self, client: Client) -> None:
        """Update an existing client. Raises KeyError if missing."""
        self._cursor.execute('SELECT * FROM clients WHERE email = ?', (client.email,))
        if self._cursor.fetchone() is None:
            raise KeyError(f"Client with email {client.email} does not exist")
        self._cursor.execute('''
            UPDATE clients
            SET name = ?, company = ?, status = ?, engagement_type = ?
            WHERE email = ?
        ''', (client.name, client.company, client.status, client.engagement_type, client.email))
        self._conn.commit()

    def delete(self, email: str) -> None:
        """Delete a client by email. Raises KeyError if missing."""
        self._cursor.execute('SELECT * FROM clients WHERE email = ?', (email,))
        if self._cursor.fetchone() is None:
            raise KeyError(f"Client with email {email} does not exist")
        self._cursor.execute('DELETE FROM clients WHERE email = ?', (email,))
        self._conn.commit()

    def close(self) -> None:
        """Close the connection."""
        self._conn.close()


class SqliteEngagementRepository:
    """SQLite-backed engagement repository."""

    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path)
        self._cursor = self._conn.cursor()
        self._create_table()

    def _create_table(self) -> None:
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS engagements (
                client_email TEXT PRIMARY KEY,
                role TEXT,
                monthly_rate REAL,
                start_date TEXT,
                end_date TEXT,
                status TEXT
            )
        ''')
        self._conn.commit()

    def add(self, engagement: Engagement) -> None:
        """Add an engagement to the repository. Raises ValueError if duplicate client_email."""
        try:
            self._cursor.execute('''
                INSERT INTO engagements (client_email, role, monthly_rate, start_date, end_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (engagement.client_email, engagement.role, engagement.monthly_rate, engagement.start_date, engagement.end_date, engagement.status))
            self._conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Engagement with client_email {engagement.client_email} already exists")

    def get(self, client_email: str) -> Engagement:
        """Get an engagement by client_email. Raises KeyError if missing."""
        self._cursor.execute('SELECT * FROM engagements WHERE client_email = ?', (client_email,))
        row = self._cursor.fetchone()
        if row is None:
            raise KeyError(f"Engagement with client_email {client_email} does not exist")
        return Engagement(
            client_email=row[0],
            role=row[1],
            monthly_rate=row[2],
            start_date=row[3],
            end_date=row[4],
            status=row[5]
        )

    def list(self) -> List[Engagement]:
        """List all engagements."""
        self._cursor.execute('SELECT * FROM engagements')
        rows = self._cursor.fetchall()
        return [Engagement(
            client_email=row[0],
            role=row[1],
            monthly_rate=row[2],
            start_date=row[3],
            end_date=row[4],
            status=row[5]
        ) for row in rows]

    def update(self, engagement: Engagement) -> None:
        """Update an existing engagement. Raises KeyError if missing."""
        self._cursor.execute('SELECT * FROM engagements WHERE client_email = ?', (engagement.client_email,))
        if self._cursor.fetchone() is None:
            raise KeyError(f"Engagement with client_email {engagement.client_email} does not exist")
        self._cursor.execute('''
            UPDATE engagements
            SET role = ?, monthly_rate = ?, start_date = ?, end_date = ?, status = ?
            WHERE client_email = ?
        ''', (engagement.role, engagement.monthly_rate, engagement.start_date, engagement.end_date, engagement.status, engagement.client_email))
        self._conn.commit()

    def delete(self, client_email: str) -> None:
        """Delete an engagement by client_email. Raises KeyError if missing."""
        self._cursor.execute('SELECT * FROM engagements WHERE client_email = ?', (client_email,))
        if self._cursor.fetchone() is None:
            raise KeyError(f"Engagement with client_email {client_email} does not exist")
        self._cursor.execute('DELETE FROM engagements WHERE client_email = ?', (client_email,))
        self._conn.commit()

    def close(self) -> None:
        """Close the connection."""
        self._conn.close()
