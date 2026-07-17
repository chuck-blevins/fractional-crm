from fractional_crm.sqlite_repository import SqliteClientRepository, SqliteEngagementRepository
from fractional_crm.web.config import get_db_path
from fractional_crm.sqlite_interaction_repository import SqliteInteractionRepository
from fractional_crm.sqlite_team_repository import SqliteTeamRepository
from fractional_crm.sqlite_integration_repository import SqliteIntegrationRepository

def get_client_repo() -> SqliteClientRepository:
    """Return a SQLite client repository bound to the configured DB path."""
    return SqliteClientRepository(get_db_path())

def get_engagement_repo() -> SqliteEngagementRepository:
    """Return a SQLite engagement repository bound to the configured DB path."""
    return SqliteEngagementRepository(get_db_path())

def get_interaction_repo() -> SqliteInteractionRepository:
    """Return a SQLite interaction repository bound to the configured DB path."""
    return SqliteInteractionRepository(get_db_path())

def get_team_repo() -> SqliteTeamRepository:
    """Return a SQLite team repository bound to the configured DB path."""
    return SqliteTeamRepository(get_db_path())

def get_integration_repo() -> SqliteIntegrationRepository:
    """Return a SQLite integration repository bound to the configured DB path."""
    return SqliteIntegrationRepository(get_db_path())
