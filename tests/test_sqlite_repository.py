import pytest
from fractional_crm.client import Client
from fractional_crm.engagement import Engagement
from fractional_crm.sqlite_repository import (
    SqliteClientRepository,
    SqliteEngagementRepository,
)


def _c(email="a@b.co", name="N", company="C", status="active", engagement_type="coo"):
    return Client(name=name, company=company, email=email,
                  status=status, engagement_type=engagement_type)


def _e(client_email="a@b.co", role="cpo", monthly_rate=10000.0,
       start_date="2026-01-01", end_date=None, status="active"):
    return Engagement(client_email=client_email, role=role, monthly_rate=monthly_rate,
                      start_date=start_date, end_date=end_date, status=status)


# ---- Client repo: schema + CRUD parity with the in-memory repo ----

def test_client_add_and_get():
    r = SqliteClientRepository()
    r.add(_c())
    got = r.get("a@b.co")
    assert got.email == "a@b.co"
    assert got.name == "N"
    assert got.company == "C"
    assert got.status == "active"
    assert got.engagement_type == "coo"


def test_client_get_returns_client_instance():
    r = SqliteClientRepository()
    r.add(_c())
    assert isinstance(r.get("a@b.co"), Client)


def test_client_add_duplicate_email_rejected():
    r = SqliteClientRepository()
    r.add(_c())
    with pytest.raises(ValueError):
        r.add(_c())


def test_client_get_missing_raises_keyerror():
    with pytest.raises(KeyError):
        SqliteClientRepository().get("missing@x.co")


def test_client_list_returns_all():
    r = SqliteClientRepository()
    r.add(_c(email="a@b.co"))
    r.add(_c(email="c@d.co"))
    assert sorted(x.email for x in r.list()) == ["a@b.co", "c@d.co"]


def test_client_list_empty():
    assert SqliteClientRepository().list() == []


def test_client_update_existing():
    r = SqliteClientRepository()
    r.add(_c(email="a@b.co", name="Old"))
    r.update(_c(email="a@b.co", name="New"))
    assert r.get("a@b.co").name == "New"


def test_client_update_missing_raises_keyerror():
    with pytest.raises(KeyError):
        SqliteClientRepository().update(_c(email="missing@x.co"))


def test_client_delete_existing():
    r = SqliteClientRepository()
    r.add(_c(email="a@b.co"))
    r.delete("a@b.co")
    with pytest.raises(KeyError):
        r.get("a@b.co")


def test_client_delete_missing_raises_keyerror():
    with pytest.raises(KeyError):
        SqliteClientRepository().delete("missing@x.co")


# ---- Engagement repo: same interface, keyed by client_email ----

def test_engagement_add_and_get():
    r = SqliteEngagementRepository()
    r.add(_e())
    got = r.get("a@b.co")
    assert got.client_email == "a@b.co"
    assert got.role == "cpo"
    assert got.monthly_rate == 10000.0
    assert got.start_date == "2026-01-01"
    assert got.end_date is None
    assert got.status == "active"


def test_engagement_get_returns_engagement_instance():
    r = SqliteEngagementRepository()
    r.add(_e())
    assert isinstance(r.get("a@b.co"), Engagement)


def test_engagement_preserves_end_date_string():
    r = SqliteEngagementRepository()
    r.add(_e(start_date="2026-01-01", end_date="2026-06-01"))
    assert r.get("a@b.co").end_date == "2026-06-01"


def test_engagement_add_duplicate_rejected():
    r = SqliteEngagementRepository()
    r.add(_e())
    with pytest.raises(ValueError):
        r.add(_e())


def test_engagement_get_missing_raises_keyerror():
    with pytest.raises(KeyError):
        SqliteEngagementRepository().get("missing@x.co")


def test_engagement_list_returns_all():
    r = SqliteEngagementRepository()
    r.add(_e(client_email="a@b.co"))
    r.add(_e(client_email="c@d.co"))
    assert sorted(x.client_email for x in r.list()) == ["a@b.co", "c@d.co"]


def test_engagement_list_empty():
    assert SqliteEngagementRepository().list() == []


def test_engagement_update_existing():
    r = SqliteEngagementRepository()
    r.add(_e(monthly_rate=10000.0))
    r.update(_e(monthly_rate=12500.0))
    assert r.get("a@b.co").monthly_rate == 12500.0


def test_engagement_update_missing_raises_keyerror():
    with pytest.raises(KeyError):
        SqliteEngagementRepository().update(_e(client_email="missing@x.co"))


def test_engagement_delete_existing():
    r = SqliteEngagementRepository()
    r.add(_e())
    r.delete("a@b.co")
    with pytest.raises(KeyError):
        r.get("a@b.co")


def test_engagement_delete_missing_raises_keyerror():
    with pytest.raises(KeyError):
        SqliteEngagementRepository().delete("missing@x.co")


# ---- Round-trip persistence to a real file on disk ----

def test_client_roundtrip_persists_to_file(tmp_path):
    db = str(tmp_path / "crm.db")
    r1 = SqliteClientRepository(db)
    r1.add(_c(email="a@b.co", name="Ada", company="AE",
              status="active", engagement_type="cpo"))
    r1.close()

    r2 = SqliteClientRepository(db)
    got = r2.get("a@b.co")
    assert got.name == "Ada"
    assert got.company == "AE"
    assert got.status == "active"
    assert got.engagement_type == "cpo"
    r2.close()


def test_engagement_roundtrip_persists_to_file(tmp_path):
    db = str(tmp_path / "crm.db")
    r1 = SqliteEngagementRepository(db)
    r1.add(_e(client_email="a@b.co", role="coo", monthly_rate=15000.0,
              start_date="2026-01-01", end_date="2026-12-31", status="active"))
    r1.close()

    r2 = SqliteEngagementRepository(db)
    got = r2.get("a@b.co")
    assert got.role == "coo"
    assert got.monthly_rate == 15000.0
    assert got.start_date == "2026-01-01"
    assert got.end_date == "2026-12-31"
    assert got.status == "active"
    r2.close()


def test_schema_created_on_init(tmp_path):
    # Constructor alone must create the schema; no separate setup call.
    db = str(tmp_path / "fresh.db")
    assert SqliteClientRepository(db).list() == []
    assert SqliteEngagementRepository(db).list() == []
