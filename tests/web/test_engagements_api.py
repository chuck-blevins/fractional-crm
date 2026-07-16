"""CRB-23: Engagements JSON API (keyed by client_email — one engagement per client)."""


def _payload(**over):
    d = {
        "client_email": "ada@acme.io",
        "role": "coo",
        "monthly_rate": 5000,
        "start_date": "2026-01-01",
        "status": "active",
        "end_date": None,
    }
    d.update(over)
    return d


def test_create_and_get(client):
    r = client.post("/api/engagements", json=_payload())
    assert r.status_code == 201
    assert r.json()["client_email"] == "ada@acme.io"
    g = client.get("/api/engagements/ada@acme.io")
    assert g.status_code == 200
    assert g.json()["monthly_rate"] == 5000


def test_list_and_filter(client):
    client.post("/api/engagements", json=_payload())
    client.post("/api/engagements", json=_payload(client_email="grace@navy.mil"))
    assert len(client.get("/api/engagements").json()) == 2
    filtered = client.get("/api/engagements?client_email=ada@acme.io").json()
    assert [e["client_email"] for e in filtered] == ["ada@acme.io"]


def test_get_missing_404(client):
    assert client.get("/api/engagements/nobody@x.io").status_code == 404


def test_create_duplicate_409(client):
    client.post("/api/engagements", json=_payload())
    assert client.post("/api/engagements", json=_payload()).status_code == 409


def test_create_rate_not_positive_422(client):
    assert client.post("/api/engagements", json=_payload(monthly_rate=0)).status_code == 422


def test_create_end_before_start_422(client):
    assert client.post("/api/engagements", json=_payload(end_date="2025-12-31")).status_code == 422


def test_update(client):
    client.post("/api/engagements", json=_payload())
    r = client.put("/api/engagements/ada@acme.io", json=_payload(monthly_rate=7500))
    assert r.status_code == 200
    assert r.json()["monthly_rate"] == 7500


def test_update_missing_404(client):
    assert client.put("/api/engagements/nobody@x.io", json=_payload(client_email="nobody@x.io")).status_code == 404


def test_delete(client):
    client.post("/api/engagements", json=_payload())
    assert client.delete("/api/engagements/ada@acme.io").status_code == 204
    assert client.get("/api/engagements/ada@acme.io").status_code == 404


def test_filter_no_match_returns_empty(client):
    client.post("/api/engagements", json=_payload())
    r = client.get("/api/engagements?client_email=nobody@x.io")
    assert r.status_code == 200
    assert r.json() == []
