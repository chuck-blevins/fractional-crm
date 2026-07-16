"""CRB-24: Interactions JSON API (log + list newest-first)."""


def _client():
    return {"name": "Ada", "company": "Acme", "email": "ada@acme.io",
            "status": "active", "engagement_type": "coo"}


def _interaction(**over):
    d = {"date": "2026-02-01", "kind": "call", "summary": "Kickoff"}
    d.update(over)
    return d


def test_log_and_list_newest_first(client):
    client.post("/api/clients", json=_client())
    assert client.post("/api/clients/ada@acme.io/interactions",
                       json=_interaction(date="2026-02-01", summary="Kickoff")).status_code == 201
    client.post("/api/clients/ada@acme.io/interactions",
                json=_interaction(date="2026-03-01", kind="email", summary="Follow up"))
    r = client.get("/api/clients/ada@acme.io/interactions")
    assert r.status_code == 200
    assert [i["summary"] for i in r.json()] == ["Follow up", "Kickoff"]


def test_post_unknown_client_404(client):
    r = client.post("/api/clients/nobody@x.io/interactions", json=_interaction())
    assert r.status_code == 404


def test_post_bad_kind_422(client):
    client.post("/api/clients", json=_client())
    assert client.post("/api/clients/ada@acme.io/interactions",
                       json=_interaction(kind="bogus")).status_code == 422


def test_post_empty_summary_422(client):
    client.post("/api/clients", json=_client())
    assert client.post("/api/clients/ada@acme.io/interactions",
                       json=_interaction(summary="   ")).status_code == 422


def test_list_empty(client):
    client.post("/api/clients", json=_client())
    assert client.get("/api/clients/ada@acme.io/interactions").json() == []
