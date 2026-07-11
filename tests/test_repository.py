import pytest
from fractional_crm.client import Client
from fractional_crm.repository import ClientRepository


def _c(email="a@b.co", name="N", company="C", status="active", engagement_type="coo"):
    return Client(name=name, company=company, email=email, status=status, engagement_type=engagement_type)


def test_add_and_get():
    r = ClientRepository()
    c = _c()
    r.add(c)
    assert r.get("a@b.co") is c


def test_add_duplicate_email_rejected():
    r = ClientRepository()
    r.add(_c())
    with pytest.raises(ValueError):
        r.add(_c())


def test_get_missing_raises_keyerror():
    with pytest.raises(KeyError):
        ClientRepository().get("missing@x.co")


def test_list_returns_all():
    r = ClientRepository()
    r.add(_c(email="a@b.co"))
    r.add(_c(email="c@d.co"))
    assert sorted(x.email for x in r.list()) == ["a@b.co", "c@d.co"]


def test_list_empty():
    assert ClientRepository().list() == []


def test_update_existing():
    r = ClientRepository()
    r.add(_c(email="a@b.co", name="Old"))
    r.update(_c(email="a@b.co", name="New"))
    assert r.get("a@b.co").name == "New"


def test_update_missing_raises_keyerror():
    with pytest.raises(KeyError):
        ClientRepository().update(_c(email="missing@x.co"))


def test_delete_existing():
    r = ClientRepository()
    r.add(_c(email="a@b.co"))
    r.delete("a@b.co")
    with pytest.raises(KeyError):
        r.get("a@b.co")


def test_delete_missing_raises_keyerror():
    with pytest.raises(KeyError):
        ClientRepository().delete("missing@x.co")
