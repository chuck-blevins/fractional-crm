import sqlite3
from typing import List, Optional
from fractional_crm.integration import Integration

class SqliteIntegrationRepository:
    def __init__(self, path: str = ":memory:") -> None:
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self) -> None:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS integrations (
            provider TEXT PRIMARY KEY,
            external_id TEXT,
            status TEXT,
            last_synced_at TEXT
        );
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def connect(self, integration: Integration) -> None:
        insert_query = """
        INSERT INTO integrations (provider, external_id, status, last_synced_at)
        VALUES (?, ?, ?, ?);
        """
        try:
            self.cursor.execute(insert_query, (integration.provider, integration.external_id, integration.status, integration.last_synced_at))
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"provider {integration.provider} already connected")

    def list(self) -> List[Integration]:
        select_query = """
        SELECT provider, external_id, status, last_synced_at FROM integrations;
        """
        self.cursor.execute(select_query)
        rows = self.cursor.fetchall()
        return [Integration(provider=r[0], external_id=r[1], status=r[2], last_synced_at=r[3]) for r in rows]

    def get(self, provider: str) -> Integration:
        select_query = """
        SELECT provider, external_id, status, last_synced_at FROM integrations WHERE provider=?;
        """
        self.cursor.execute(select_query, (provider,))
        row = self.cursor.fetchone()
        if row is None:
            raise KeyError(provider)
        return Integration(provider=row[0], external_id=row[1], status=row[2], last_synced_at=row[3])

    def delete(self, provider: str) -> None:
        select_query = """
        SELECT 1 FROM integrations WHERE provider=?;
        """
        self.cursor.execute(select_query, (provider,))
        if self.cursor.fetchone() is None:
            raise KeyError(provider)
        delete_query = """
        DELETE FROM integrations WHERE provider=?
        """
        self.cursor.execute(delete_query, (provider,))
        self.connection.commit()

    def update(self, integration: Integration) -> None:
        update_query = """
        UPDATE integrations
        SET external_id=?, status=?, last_synced_at=?
        WHERE provider=?
        """
        self.cursor.execute(update_query, (integration.external_id, integration.status, integration.last_synced_at, integration.provider))
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
