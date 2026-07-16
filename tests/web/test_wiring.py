"""CRB-21: config + SQLite wiring via CRM_DB_PATH."""
import pytest

from fractional_crm.client import Client
from fractional_crm.web.config import get_db_path
from fractional_crm.web.deps import get_client_repo


def _client() -> Client:
    return Client(name="Ada", company="Acme", email="ada@acme.io",
                  status="active", engagement_type="coo")


def test_db_path_default_and_env(monkeypatch, tmp_path):
    monkeypatch.delenv("CRM_DB_PATH", raising=False)
    assert get_db_path() == "crm.db"
    p = str(tmp_path / "x.db")
    monkeypatch.setenv("CRM_DB_PATH", p)
    assert get_db_path() == p


def test_repo_persists_to_configured_path(monkeypatch, tmp_path):
    monkeypatch.setenv("CRM_DB_PATH", str(tmp_path / "crm.db"))
    repo = get_client_repo()
    repo.add(_client())
    repo.close()
    fresh = get_client_repo()          # new connection, same path
    assert fresh.get("ada@acme.io").name == "Ada"
    fresh.close()


def test_paths_are_isolated(monkeypatch, tmp_path):
    monkeypatch.setenv("CRM_DB_PATH", str(tmp_path / "a.db"))
    get_client_repo().add(_client())
    monkeypatch.setenv("CRM_DB_PATH", str(tmp_path / "b.db"))
    with pytest.raises(KeyError):
        get_client_repo().get("ada@acme.io")


def test_client_fixture_has_isolated_empty_db(client):
    assert client.get("/health").status_code == 200
