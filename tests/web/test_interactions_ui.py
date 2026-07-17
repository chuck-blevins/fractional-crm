"""CRB-32 acceptance: client detail page with an interactions timeline + log form.

The timeline reads the interactions API (newest first) and the log form creates an
interaction, re-rendering accessibly on an empty summary. The interactions repo already
sorts newest-first; the ordering test inserts out of order to also pin the template.
"""


def _seed_client(client, **over):
    """Create a client via the JSON API."""
    payload = {"name": "Ada Lovelace", "company": "Acme", "email": "ada@acme.io",
               "status": "active", "engagement_type": "coo"}
    payload.update(over)
    r = client.post("/api/clients", json=payload)
    assert r.status_code == 201, r.text
    return payload


def _log(client, email, **over):
    """Log an interaction via the JSON API."""
    d = {"date": "2026-02-01", "kind": "call", "summary": "Kickoff"}
    d.update(over)
    r = client.post(f"/api/clients/{email}/interactions", json=d)
    assert r.status_code == 201, r.text


def test_detail_page_shows_client_and_timeline_newest_first(client):
    _seed_client(client, email="ada@acme.io", name="Ada Lovelace")
    # Insert OLD first, then NEW — newest-first must reverse insertion order.
    _log(client, "ada@acme.io", date="2026-01-01", kind="note", summary="OLD note")
    _log(client, "ada@acme.io", date="2026-03-01", kind="email", summary="NEW email")
    html = client.get("/clients/ada@acme.io").text
    assert "Ada Lovelace" in html                 # it is the client's detail page
    assert "OLD note" in html and "NEW email" in html
    # Newest first: the newer entry appears before the older one in document order.
    assert html.index("NEW email") < html.index("OLD note")


def test_empty_state_when_no_interactions(client):
    _seed_client(client, email="ada@acme.io")
    html = client.get("/clients/ada@acme.io").text
    assert "no interactions" in html.lower()


def test_log_form_kind_select_limited_to_allowed(client):
    _seed_client(client, email="ada@acme.io")
    html = client.get("/clients/ada@acme.io").text
    for kind in ("call", "email", "meeting", "note"):
        assert f'value="{kind}"' in html
    assert 'value="tweet"' not in html


def test_log_empty_summary_rerenders_error_and_does_not_persist(client):
    _seed_client(client, email="ada@acme.io")
    r = client.post("/clients/ada@acme.io/interactions",
                    data={"date": "2026-02-01", "kind": "call", "summary": "   "},
                    follow_redirects=False)
    assert r.status_code == 200
    lower = r.text.lower()
    assert 'role="alert"' in lower
    assert "summary" in lower
    # Nothing persisted.
    assert client.get("/api/clients/ada@acme.io/interactions").json() == []


def test_valid_log_persists_and_appears_on_timeline(client):
    _seed_client(client, email="ada@acme.io")
    r = client.post("/clients/ada@acme.io/interactions",
                    data={"date": "2026-04-01", "kind": "meeting", "summary": "Quarterly review"},
                    follow_redirects=False)
    assert r.status_code in (200, 302, 303, 307)
    api = client.get("/api/clients/ada@acme.io/interactions").json()
    assert [i["summary"] for i in api] == ["Quarterly review"]
    assert "Quarterly review" in client.get("/clients/ada@acme.io").text


def test_detail_unknown_client_404(client):
    assert client.get("/clients/nobody@x.io").status_code == 404
