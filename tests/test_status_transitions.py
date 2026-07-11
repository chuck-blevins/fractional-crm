import pytest
from fractional_crm.client import Client


def _c(status="prospect"):
    return Client(name="N", company="C", email="a@b.co", status=status, engagement_type="coo")


def test_prospect_to_active():
    c = _c("prospect"); c.transition_to("active"); assert c.status == "active"


def test_active_to_paused():
    c = _c("active"); c.transition_to("paused"); assert c.status == "paused"


def test_paused_to_active():
    c = _c("paused"); c.transition_to("active"); assert c.status == "active"


def test_active_to_closed():
    c = _c("active"); c.transition_to("closed"); assert c.status == "closed"


def test_paused_to_closed():
    c = _c("paused"); c.transition_to("closed"); assert c.status == "closed"


def test_illegal_prospect_to_closed():
    with pytest.raises(ValueError):
        _c("prospect").transition_to("closed")


def test_illegal_prospect_to_paused():
    with pytest.raises(ValueError):
        _c("prospect").transition_to("paused")


def test_illegal_closed_to_active():
    with pytest.raises(ValueError):
        _c("closed").transition_to("active")


def test_illegal_active_to_prospect():
    with pytest.raises(ValueError):
        _c("active").transition_to("prospect")


def test_transition_to_unknown_status_rejected():
    with pytest.raises(ValueError):
        _c("active").transition_to("lead")


def test_illegal_transition_leaves_status_unchanged():
    c = _c("prospect")
    with pytest.raises(ValueError):
        c.transition_to("closed")
    assert c.status == "prospect"
