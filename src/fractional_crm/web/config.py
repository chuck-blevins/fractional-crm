import os

def get_db_path() -> str:
    """Return the SQLite DB path from the CRM_DB_PATH env var, defaulting to crm.db."""
    return os.environ.get("CRM_DB_PATH", "crm.db")
