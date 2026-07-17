"""CRB-25: Integrations JSON API."""


def _integ(**over):
    d = {"provider": "slack", "external_id": "T123"}
    d.update(over); return d


def test_connect_and_list(client):
    assert client.post("/api/integrations", json=_integ()).status_code == 201
    assert "slack" in [i["provider"] for i in client.get("/api/integrations").json()]


def test_connect_duplicate_409(client):
    client.post("/api/integrations", json=_integ())
    assert client.post("/api/integrations", json=_integ(external_id="T456")).status_code == 409


def test_connect_bad_provider_422(client):
    assert client.post("/api/integrations", json=_integ(provider="bogus")).status_code == 422


def test_disconnect(client):
    client.post("/api/integrations", json=_integ())
    assert client.delete("/api/integrations/slack").status_code == 204
    assert "slack" not in [i["provider"] for i in client.get("/api/integrations").json()]


def test_disconnect_unknown_404(client):
    assert client.delete("/api/integrations/github").status_code == 404


def test_sync(client):
    client.post("/api/integrations", json=_integ())
    r = client.post("/api/integrations/slack/sync", json={"timestamp": "2026-07-11T12:00:00"})
    assert r.status_code == 200
    assert r.json()["last_synced_at"] == "2026-07-11T12:00:00"
    assert r.json()["status"] == "connected"


def test_sync_unknown_404(client):
    assert client.post("/api/integrations/github/sync", json={"timestamp": "2026-07-11T12:00:00"}).status_code == 404
