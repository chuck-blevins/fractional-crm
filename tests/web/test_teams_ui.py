"""CRB-33 acceptance (part 1): Teams UI — team list, member roster, add-member form.

Mirrors the Clients/Engagements UI conventions (CRB-30/31): a gated server-rendered router,
HTMX fragment on ``HX-Request`` and a 303 redirect otherwise, domain ``ValueError`` re-rendered
accessibly at 200 with the entered values preserved, ``KeyError`` -> 404.

The role ``<select>`` is driven from ``team.ROLES`` so the template never re-encodes the domain.
"""
import pytest

from htmlcheck import assert_valid_html


def _seed_team(client, name="Platform"):
    """Create a team via the JSON API and return its id."""
    r = client.post("/api/teams", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _seed_member(client, team_id, **over):
    """Add a member via the JSON API."""
    payload = {"name": "Ada Lovelace", "email": "ada@acme.io", "role": "admin"}
    payload.update(over)
    r = client.post(f"/api/teams/{team_id}/members", json=payload)
    assert r.status_code == 201, r.text
    return payload


def _members(client, team_id):
    """Read the member roster back through the JSON API."""
    return client.get(f"/api/teams/{team_id}/members").json()


# ----------------------------------------------------------------------------- team list


def test_teams_list_renders_seeded_teams(client):
    _seed_team(client, "Platform")
    _seed_team(client, "Design")
    r = client.get("/teams")
    assert r.status_code == 200
    assert "Platform" in r.text and "Design" in r.text


def test_teams_list_empty_state(client):
    r = client.get("/teams")
    assert r.status_code == 200
    assert "no teams" in r.text.lower()


def test_teams_list_links_to_each_team(client):
    team_id = _seed_team(client)
    assert f'href="/teams/{team_id}"' in client.get("/teams").text


def test_create_team_persists_and_redirects(client):
    r = client.post("/teams", data={"name": "Platform"}, follow_redirects=False)
    assert r.status_code in (302, 303, 307)
    assert [t["name"] for t in client.get("/api/teams").json()] == ["Platform"]


def test_create_team_with_blank_name_rerenders_accessibly(client):
    r = client.post("/teams", data={"name": "   "}, follow_redirects=False)
    assert r.status_code == 200
    assert 'role="alert"' in r.text.lower()
    assert client.get("/api/teams").json() == []


# --------------------------------------------------------------------------- team detail


def test_team_detail_shows_name_and_members(client):
    team_id = _seed_team(client, "Platform")
    _seed_member(client, team_id, name="Ada Lovelace", email="ada@acme.io", role="admin")
    _seed_member(client, team_id, name="Grace Hopper", email="grace@navy.mil", role="member")
    html = client.get(f"/teams/{team_id}").text
    assert "Platform" in html
    assert "Ada Lovelace" in html and "ada@acme.io" in html and "admin" in html
    assert "Grace Hopper" in html and "grace@navy.mil" in html


def test_team_detail_empty_roster(client):
    team_id = _seed_team(client)
    assert "no members" in client.get(f"/teams/{team_id}").text.lower()


def test_team_detail_unknown_team_404(client):
    assert client.get("/teams/4242").status_code == 404


def test_role_select_limited_to_domain_roles(client):
    """The <select> is driven from team.ROLES — no extra values, no missing ones."""
    from fractional_crm.team import ROLES

    html = client.get(f"/teams/{_seed_team(client)}").text
    for role in ROLES:
        assert f'value="{role}"' in html
    assert 'value="owner"' not in html


# ---------------------------------------------------------------------------- add member


def test_add_member_persists_and_redirects(client):
    team_id = _seed_team(client)
    r = client.post(f"/teams/{team_id}/members",
                    data={"name": "Ada Lovelace", "email": "ada@acme.io", "role": "admin"},
                    follow_redirects=False)
    assert r.status_code in (200, 302, 303, 307)
    assert [m["email"] for m in _members(client, team_id)] == ["ada@acme.io"]
    assert "Ada Lovelace" in client.get(f"/teams/{team_id}").text


def test_add_duplicate_member_rerenders_error_and_does_not_persist(client):
    """The headline case from the spec: a duplicate (team, email) is an inline, accessible error."""
    team_id = _seed_team(client)
    _seed_member(client, team_id, email="ada@acme.io")
    r = client.post(f"/teams/{team_id}/members",
                    data={"name": "Ada L", "email": "ada@acme.io", "role": "member"},
                    follow_redirects=False)
    assert r.status_code == 200
    assert 'role="alert"' in r.text.lower()
    # Still exactly one member, and the original record is untouched.
    roster = _members(client, team_id)
    assert len(roster) == 1
    assert roster[0]["name"] == "Ada Lovelace" and roster[0]["role"] == "admin"


def test_add_member_error_preserves_entered_values(client):
    team_id = _seed_team(client)
    _seed_member(client, team_id, email="ada@acme.io")
    html = client.post(f"/teams/{team_id}/members",
                       data={"name": "Ada L", "email": "ada@acme.io", "role": "guest"},
                       follow_redirects=False).text
    assert 'value="Ada L"' in html and 'value="ada@acme.io"' in html


@pytest.mark.parametrize("field, value", [("email", "not-an-email"), ("name", "   ")])
def test_add_member_invalid_input_rerenders_accessibly(client, field, value):
    team_id = _seed_team(client)
    data = {"name": "Ada Lovelace", "email": "ada@acme.io", "role": "admin"}
    data[field] = value
    r = client.post(f"/teams/{team_id}/members", data=data, follow_redirects=False)
    assert r.status_code == 200
    assert 'role="alert"' in r.text.lower()
    assert _members(client, team_id) == []


def test_add_member_to_unknown_team_404(client):
    r = client.post("/teams/4242/members",
                    data={"name": "Ada", "email": "ada@acme.io", "role": "admin"},
                    follow_redirects=False)
    assert r.status_code == 404


def test_htmx_add_member_returns_roster_fragment(client):
    """HTMX swaps just the roster; the response must not be a whole document."""
    team_id = _seed_team(client)
    r = client.post(f"/teams/{team_id}/members",
                    data={"name": "Ada Lovelace", "email": "ada@acme.io", "role": "admin"},
                    headers={"HX-Request": "true"}, follow_redirects=False)
    assert r.status_code == 200
    assert "Ada Lovelace" in r.text
    assert "<html" not in r.text.lower()
    assert_valid_html(r.text, context="HTMX roster fragment", fragment=True)


# ------------------------------------------------------------------------------- markup


def test_team_pages_are_valid_html(client):
    """CRB-32 follow-up: new pages are held to the same structural standard."""
    team_id = _seed_team(client)
    _seed_member(client, team_id)
    assert_valid_html(client.get("/teams").text, context="GET /teams")
    assert_valid_html(client.get(f"/teams/{team_id}").text, context="GET /teams/{id}")
