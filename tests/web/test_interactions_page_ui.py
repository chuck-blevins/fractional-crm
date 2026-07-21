"""CRB-40 acceptance: the global /interactions feed page (all clients, newest first).

Distinct from test_interactions_ui.py (the per-client timeline on the detail page).
This page is a single global list of every interaction across all clients.
"""
from htmlcheck import assert_valid_html


def _seed_client(client, email, name="Ada"):
    """Create a client via the JSON API."""
    r = client.post("/api/clients", json={"name": name, "company": "Co", "email": email,
                                          "status": "active", "engagement_type": "coo"})
    assert r.status_code == 201, r.text


def _log(client, email, date, kind, summary):
    """Log an interaction via the JSON API."""
    r = client.post(f"/api/clients/{email}/interactions",
                    json={"date": date, "kind": kind, "summary": summary})
    assert r.status_code == 201, r.text


def test_page_ok(client):
    assert client.get("/interactions").status_code == 200


def test_lists_across_clients_newest_first(client):
    _seed_client(client, "ada@acme.io")
    _seed_client(client, "bob@beta.io")
    _log(client, "ada@acme.io", "2026-01-01", "call", "Older with Ada")
    _log(client, "bob@beta.io", "2026-06-01", "email", "Newer with Bob")
    html = client.get("/interactions").text
    assert "Older with Ada" in html
    assert "Newer with Bob" in html
    assert html.index("Newer with Bob") < html.index("Older with Ada")


def test_shows_client_email(client):
    _seed_client(client, "ada@acme.io")
    _log(client, "ada@acme.io", "2026-01-01", "note", "Hi")
    assert "ada@acme.io" in client.get("/interactions").text


def test_empty_state(client):
    assert "No interactions" in client.get("/interactions").text


def test_valid_html(client):
    _seed_client(client, "ada@acme.io")
    _log(client, "ada@acme.io", "2026-01-01", "note", "Hi")
    assert_valid_html(client.get("/interactions").text, context="GET /interactions")
