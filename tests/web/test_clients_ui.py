"""CRB-30 acceptance: Clients UI (list / create / status transitions)."""


def _seed(client, **over):
    """Create a client via the JSON API and return the payload."""
    payload = {"name": "Ada Lovelace", "company": "Acme", "email": "ada@acme.io",
               "status": "active", "engagement_type": "coo"}
    payload.update(over)
    r = client.post("/api/clients", json=payload)
    assert r.status_code == 201, r.text
    return payload


def test_clients_list_renders_seeded_rows(client):
    _seed(client, email="ada@acme.io", name="Ada Lovelace")
    _seed(client, email="grace@navy.mil", name="Grace Hopper", status="prospect")
    r = client.get("/clients")
    assert r.status_code == 200
    html = r.text
    assert "<table" in html.lower()
    assert "Ada Lovelace" in html and "ada@acme.io" in html
    assert "Grace Hopper" in html and "grace@navy.mil" in html


def test_create_bad_email_rerenders_error_and_does_not_persist(client):
    r = client.post(
        "/clients",
        data={"name": "Bad", "company": "X", "email": "not-an-email",
              "status": "prospect", "engagement_type": "coo"},
        follow_redirects=False,
    )
    # Re-renders the form with an accessible error (200), not a redirect.
    assert r.status_code == 200
    lower = r.text.lower()
    assert "error" in lower or "invalid" in lower
    # Nothing persisted.
    assert client.get("/api/clients/not-an-email").status_code == 404
    assert all(c["email"] != "not-an-email" for c in client.get("/api/clients").json())


def test_valid_create_persists_and_redirects(client):
    r = client.post(
        "/clients",
        data={"name": "Katherine Johnson", "company": "NASA", "email": "kj@nasa.gov",
              "status": "prospect", "engagement_type": "advisor"},
        follow_redirects=False,
    )
    assert r.status_code in (302, 303, 307)
    assert "/clients" in r.headers["location"]
    assert client.get("/api/clients/kj@nasa.gov").status_code == 200


def test_status_form_offers_only_allowed_transitions_for_active(client):
    _seed(client, email="ada@acme.io", status="active")
    html = client.get("/clients").text
    # An active client may move to paused or closed — never (back) to prospect.
    assert 'value="paused"' in html
    assert 'value="closed"' in html
    assert 'value="prospect"' not in html


def test_status_transition_updates_client(client):
    _seed(client, email="ada@acme.io", status="active")
    r = client.post("/clients/ada@acme.io/status", data={"status": "paused"},
                    follow_redirects=False)
    assert r.status_code in (302, 303, 307)
    assert client.get("/api/clients/ada@acme.io").json()["status"] == "paused"
