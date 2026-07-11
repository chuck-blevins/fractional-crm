import pytest
from fractional_crm.interaction import Interaction
from fractional_crm.interaction_log import InteractionLog


def _i(**kw):
    d = dict(client_email="a@b.co", date="2026-01-01",
             kind="call", summary="Kickoff call")
    d.update(kw)
    return Interaction(**d)


# --- Interaction model validation ---

def test_valid():
    i = _i()
    assert i.client_email == "a@b.co"
    assert i.date == "2026-01-01"
    assert i.kind == "call"
    assert i.summary == "Kickoff call"


def test_allowed_kinds():
    for k in ["call", "email", "meeting", "note"]:
        assert _i(kind=k).kind == k


def test_invalid_kind_rejected():
    for bad in ["text", "sms", "", "CALL"]:
        with pytest.raises(ValueError):
            _i(kind=bad)


def test_invalid_email_rejected():
    for bad in ["bad-email", "a@", "@b.co", "a b@c.co", ""]:
        with pytest.raises(ValueError):
            _i(client_email=bad)


def test_invalid_date_rejected():
    for bad in ["not-a-date", "2026-13-01", "2026-01-32", "01/01/2026", ""]:
        with pytest.raises(ValueError):
            _i(date=bad)


def test_date_stored_as_original_iso_string():
    i = _i(date="2026-03-15")
    assert i.date == "2026-03-15"
    assert isinstance(i.date, str)


def test_summary_must_be_non_empty():
    for bad in ["", "   ", "\t\n"]:
        with pytest.raises(ValueError):
            _i(summary=bad)


def test_summary_is_stripped():
    assert _i(summary="  Had a chat  ").summary == "Had a chat"


# --- InteractionLog repo ---

def test_add_and_list_for_client():
    log = InteractionLog()
    i = _i()
    log.add(i)
    assert log.list_for_client("a@b.co") == [i]


def test_list_for_client_empty_when_none():
    assert InteractionLog().list_for_client("nobody@x.co") == []


def test_list_for_client_filters_by_email():
    log = InteractionLog()
    a1 = _i(client_email="a@b.co", date="2026-01-01")
    b1 = _i(client_email="c@d.co", date="2026-02-01")
    log.add(a1)
    log.add(b1)
    assert log.list_for_client("a@b.co") == [a1]
    assert log.list_for_client("c@d.co") == [b1]


def test_list_for_client_sorted_by_date_desc():
    log = InteractionLog()
    old = _i(date="2026-01-01", summary="old")
    mid = _i(date="2026-03-01", summary="mid")
    new = _i(date="2026-06-01", summary="new")
    log.add(mid)
    log.add(old)
    log.add(new)
    assert log.list_for_client("a@b.co") == [new, mid, old]
    assert [x.date for x in log.list_for_client("a@b.co")] == [
        "2026-06-01", "2026-03-01", "2026-01-01"]


def test_add_returns_none_and_multiple_clients_independent():
    log = InteractionLog()
    a1 = _i(client_email="a@b.co", date="2026-01-01")
    a2 = _i(client_email="a@b.co", date="2026-05-01")
    b1 = _i(client_email="c@d.co", date="2026-02-01")
    assert log.add(a1) is None
    log.add(b1)
    log.add(a2)
    assert log.list_for_client("a@b.co") == [a2, a1]
    assert log.list_for_client("c@d.co") == [b1]
