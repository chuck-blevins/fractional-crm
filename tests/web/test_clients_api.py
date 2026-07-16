"""CRB-22: Clients JSON API (CRUD + status transition)."""


def _payload(**over):
    d = {
        "name": "Ada Lovelace",
        "company": "Acme",
        "email": "ada@acme.io",
        "status": "active",
        "engagement_type": "coo",
    }
    d.update(over)
    return d


def test_create_and_get(client):
    r = client.post("/api/clients", json=_payload())
    assert r.status_code == 201
    assert r.json()["email"] == "ada@acme.io"
    g = client.get("/api/clients/ada@acme.io")
    assert g.status_code == 200
    assert g.json()["name"] == "Ada Lovelace"


def test_list(client):
    client.post("/api/clients", json=_payload())
    client.post("/api/clients", json=_payload(email="grace@navy.mil", name="Grace"))
    r = client.get("/api/clients")
    assert r.status_code == 200
    assert {"ada@acme.io", "grace@navy.mil"} <= {c["email"] for c in r.json()}


def test_get_missing_404(client):
    assert client.get("/api/clients/nobody@x.io").status_code == 404


def test_create_duplicate_409(client):
    client.post("/api/clients", json=_payload())
    assert client.post("/api/clients", json=_payload()).status_code == 409


def test_create_invalid_email_422(client):
    assert client.post("/api/clients", json=_payload(email="not-an-email")).status_code == 422


def test_update(client):
    client.post("/api/clients", json=_payload())
    r = client.put("/api/clients/ada@acme.io", json=_payload(company="NewCo"))
    assert r.status_code == 200
    assert r.json()["company"] == "NewCo"


def test_update_missing_404(client):
    assert client.put("/api/clients/nobody@x.io", json=_payload(email="nobody@x.io")).status_code == 404


def test_delete(client):
    client.post("/api/clients", json=_payload())
    assert client.delete("/api/clients/ada@acme.io").status_code == 204
    assert client.get("/api/clients/ada@acme.io").status_code == 404


def test_delete_missing_404(client):
    assert client.delete("/api/clients/nobody@x.io").status_code == 404


def test_status_transition_allowed(client):
    client.post("/api/clients", json=_payload(status="active"))
    r = client.post("/api/clients/ada@acme.io/status", json={"status": "paused"})
    assert r.status_code == 200
    assert r.json()["status"] == "paused"


def test_status_transition_disallowed_422(client):
    client.post("/api/clients", json=_payload(status="active"))
    r = client.post("/api/clients/ada@acme.io/status", json={"status": "prospect"})
    assert r.status_code == 422
    assert client.get("/api/clients/ada@acme.io").json()["status"] == "active"
