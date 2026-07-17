"""CRB-25: Teams + members JSON API."""


def _team(): return {"name": "Delivery"}


def _member(**over):
    d = {"name": "Ada", "email": "ada@acme.io", "role": "admin"}
    d.update(over); return d


def _make_team(client):
    return client.post("/api/teams", json=_team()).json()["id"]


def test_create_team_and_list(client):
    r = client.post("/api/teams", json=_team())
    assert r.status_code == 201
    tid = r.json()["id"]
    assert any(t["id"] == tid and t["name"] == "Delivery" for t in client.get("/api/teams").json())


def test_add_member_and_list(client):
    tid = _make_team(client)
    assert client.post(f"/api/teams/{tid}/members", json=_member()).status_code == 201
    assert [m["email"] for m in client.get(f"/api/teams/{tid}/members").json()] == ["ada@acme.io"]


def test_add_member_duplicate_409(client):
    tid = _make_team(client)
    client.post(f"/api/teams/{tid}/members", json=_member())
    assert client.post(f"/api/teams/{tid}/members", json=_member(name="Ada2", role="member")).status_code == 409


def test_add_member_bad_role_422(client):
    tid = _make_team(client)
    assert client.post(f"/api/teams/{tid}/members", json=_member(role="boss")).status_code == 422


def test_members_role_filter(client):
    tid = _make_team(client)
    client.post(f"/api/teams/{tid}/members", json=_member())
    client.post(f"/api/teams/{tid}/members", json=_member(name="Bob", email="bob@acme.io", role="member"))
    assert [m["email"] for m in client.get(f"/api/teams/{tid}/members?role=admin").json()] == ["ada@acme.io"]


def test_members_unknown_team_404(client):
    assert client.post("/api/teams/999/members", json=_member()).status_code == 404
