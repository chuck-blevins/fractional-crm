import pytest
from fractional_crm.client import Client


def test_valid_client():
    c = Client(name="Ada Lovelace", company="Analytical Engines",
               email="ada@analytical.io", status="active", engagement_type="cpo")
    assert c.name == "Ada Lovelace"
    assert c.company == "Analytical Engines"
    assert c.email == "ada@analytical.io"
    assert c.status == "active"
    assert c.engagement_type == "cpo"


def test_name_stripped():
    c = Client(name="  Grace Hopper  ", company="Navy",
               email="grace@navy.mil", status="prospect", engagement_type="advisor")
    assert c.name == "Grace Hopper"


def test_empty_name_rejected():
    with pytest.raises(ValueError):
        Client(name="   ", company="X", email="a@b.co",
               status="prospect", engagement_type="advisor")


def test_invalid_emails_rejected():
    for bad in ["not-an-email", "a@b", "@b.co", "a@.co", "a b@c.co", ""]:
        with pytest.raises(ValueError):
            Client(name="N", company="C", email=bad,
                   status="active", engagement_type="coo")


def test_valid_emails_accepted():
    for good in ["a@b.co", "first.last@sub.domain.com", "x_y@z.io"]:
        c = Client(name="N", company="C", email=good,
                   status="active", engagement_type="coo")
        assert c.email == good


def test_allowed_status_values():
    for s in ["prospect", "active", "paused", "closed"]:
        assert Client(name="N", company="C", email="a@b.co",
                      status=s, engagement_type="coo").status == s


def test_invalid_status_rejected():
    with pytest.raises(ValueError):
        Client(name="N", company="C", email="a@b.co",
               status="lead", engagement_type="coo")


def test_allowed_engagement_types():
    for e in ["coo", "cpo", "advisor"]:
        assert Client(name="N", company="C", email="a@b.co",
                      status="active", engagement_type=e).engagement_type == e


def test_invalid_engagement_type_rejected():
    with pytest.raises(ValueError):
        Client(name="N", company="C", email="a@b.co",
               status="active", engagement_type="ceo")
