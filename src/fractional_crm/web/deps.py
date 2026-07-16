from fractional_crm.sqlite_repository import SqliteClientRepository, SqliteEngagementRepository
from fractional_crm.web.config import get_db_path

def get_client_repo() -> SqliteClientRepository:
    """Return a SQLite client repository bound to the configured DB path."""
    return SqliteClientRepository(get_db_path())

def get_engagement_repo() -> SqliteEngagementRepository:
    """Return a SQLite engagement repository bound to the configured DB path."""
    return SqliteEngagementRepository(get_db_path())
