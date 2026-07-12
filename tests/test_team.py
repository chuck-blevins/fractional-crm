import pytest
from fractional_crm.team import TeamMember, Team


def _m(**kw):
    d = dict(name="Alice", email="alice@acme.co", role="admin")
    d.update(kw)
    return TeamMember(**d)


# ---- TeamMember ----

def test_member_valid():
    m = _m()
    assert m.name == "Alice"
    assert m.email == "alice@acme.co"
    assert m.role == "admin"


def test_member_name_stripped():
    assert _m(name="  Bob  ").name == "Bob"


def test_member_empty_name_rejected():
    for bad in ["", "   "]:
        with pytest.raises(ValueError):
            _m(name=bad)


def test_member_allowed_roles():
    for r in ["admin", "member", "guest"]:
        assert _m(role=r).role == r


def test_member_invalid_role_rejected():
    for bad in ["owner", "Admin", "superuser", ""]:
        with pytest.raises(ValueError):
            _m(role=bad)


def test_member_invalid_email_rejected():
    for bad in ["bad-email", "a@b", "@acme.co", "alice@", "a b@acme.co", ""]:
        with pytest.raises(ValueError):
            _m(email=bad)


# ---- Team ----

def test_team_valid():
    t = Team(name="Product")
    assert t.name == "Product"
    assert t.list_members() == []


def test_team_name_stripped():
    assert Team(name="  Ops  ").name == "Ops"


def test_team_empty_name_rejected():
    for bad in ["", "   "]:
        with pytest.raises(ValueError):
            Team(name=bad)


def test_team_add_and_list_members():
    t = Team(name="Product")
    a = _m(name="Alice", email="alice@acme.co", role="admin")
    b = _m(name="Bob", email="bob@acme.co", role="member")
    t.add_member(a)
    t.add_member(b)
    assert t.list_members() == [a, b]


def test_team_add_duplicate_email_rejected():
    t = Team(name="Product")
    t.add_member(_m(email="alice@acme.co"))
    with pytest.raises(ValueError):
        t.add_member(_m(name="Other", email="alice@acme.co", role="guest"))


def test_team_get_member():
    t = Team(name="Product")
    a = _m(email="alice@acme.co")
    t.add_member(a)
    assert t.get_member("alice@acme.co") is a


def test_team_get_missing_member_raises_keyerror():
    t = Team(name="Product")
    with pytest.raises(KeyError):
        t.get_member("nobody@acme.co")


def test_team_remove_member():
    t = Team(name="Product")
    t.add_member(_m(email="alice@acme.co"))
    t.remove_member("alice@acme.co")
    assert t.list_members() == []


def test_team_remove_missing_member_raises_keyerror():
    t = Team(name="Product")
    with pytest.raises(KeyError):
        t.remove_member("nobody@acme.co")


def test_team_members_with_role():
    t = Team(name="Product")
    a = _m(name="Alice", email="alice@acme.co", role="admin")
    b = _m(name="Bob", email="bob@acme.co", role="member")
    c = _m(name="Cara", email="cara@acme.co", role="member")
    for m in (a, b, c):
        t.add_member(m)
    assert t.members_with_role("member") == [b, c]
    assert t.members_with_role("admin") == [a]
    assert t.members_with_role("guest") == []


def test_team_members_with_role_rejects_invalid_role():
    t = Team(name="Product")
    with pytest.raises(ValueError):
        t.members_with_role("owner")
