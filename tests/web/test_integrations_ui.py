"""CRB-33 acceptance (part 2): Integrations UI — connect, disconnect, sync now.

The page lists the FIXED provider set from ``integration.PROVIDERS`` (not just the connected
ones), so an unconnected provider still has a row and a connect form. Rows carry
``data-testid="integration-<provider>"`` hooks so the assertions do not depend on layout,
the same convention the CRB-31 dashboard widgets use.

"Sync now" timestamps server-side. The router exposes ``now_iso()`` as a seam so tests can pin
the clock — the JSON API takes a caller-supplied timestamp, but a UI button must not.
"""
import pytest

from fractional_crm.integration import PROVIDERS
from htmlcheck import assert_valid_html


@pytest.fixture
def pinned_clock(monkeypatch):
    """Freeze the router's clock so the last-synced label is assertable."""
    from fractional_crm.web import pages_integrations

    monkeypatch.setattr(pages_integrations, "now_iso", lambda: "2026-07-18T09:30:00")
    return "2026-07-18T09:30:00"


def _connect(client, provider="slack", external_id="T12345"):
    """Connect a provider through the UI form."""
    return client.post("/integrations/connect",
                       data={"provider": provider, "external_id": external_id},
                       follow_redirects=False)


def _api_list(client):
    """Read integrations back through the JSON API, keyed by provider."""
    return {i["provider"]: i for i in client.get("/api/integrations").json()}


# ------------------------------------------------------------------------------- listing


def test_lists_every_provider_even_when_none_connected(client):
    """All six providers get a row whether or not they are connected."""
    html = client.get("/integrations").text
    for provider in PROVIDERS:
        assert f'data-testid="integration-{provider}"' in html


def test_unconnected_provider_shows_not_connected(client):
    assert "not connected" in client.get("/integrations").text.lower()


def test_connected_provider_shows_status_and_external_id(client):
    _connect(client, "slack", "T12345")
    html = client.get("/integrations").text
    assert "connected" in html.lower()
    assert "T12345" in html


def test_provider_select_limited_to_domain_providers(client):
    html = client.get("/integrations").text
    for provider in PROVIDERS:
        assert f'value="{provider}"' in html
    assert 'value="myspace"' not in html


# ------------------------------------------------------------------------------- connect


def test_connect_persists_and_redirects(client):
    r = _connect(client, "github", "org/repo")
    assert r.status_code in (302, 303, 307)
    entry = _api_list(client)["github"]
    assert entry["external_id"] == "org/repo"
    assert entry["status"] == "connected"


def test_connect_with_blank_external_id_rerenders_accessibly(client):
    r = client.post("/integrations/connect",
                    data={"provider": "slack", "external_id": "   "},
                    follow_redirects=False)
    assert r.status_code == 200
    assert 'role="alert"' in r.text.lower()
    assert _api_list(client) == {}


def test_connect_unknown_provider_rerenders_accessibly(client):
    r = client.post("/integrations/connect",
                    data={"provider": "myspace", "external_id": "x"},
                    follow_redirects=False)
    assert r.status_code == 200
    assert 'role="alert"' in r.text.lower()
    assert _api_list(client) == {}


def test_connecting_an_already_connected_provider_rerenders_accessibly(client):
    _connect(client, "slack", "T12345")
    r = _connect(client, "slack", "T99999")
    assert r.status_code == 200
    assert 'role="alert"' in r.text.lower()
    assert _api_list(client)["slack"]["external_id"] == "T12345"  # unchanged


# ---------------------------------------------------------------------------- disconnect


def test_disconnect_removes_the_integration(client):
    _connect(client, "slack", "T12345")
    r = client.post("/integrations/slack/disconnect", follow_redirects=False)
    assert r.status_code in (200, 302, 303, 307)
    assert "slack" not in _api_list(client)
    assert "not connected" in client.get("/integrations").text.lower()


def test_disconnect_unknown_provider_404(client):
    assert client.post("/integrations/slack/disconnect", follow_redirects=False).status_code == 404


# ---------------------------------------------------------------------------- sync now


def test_sync_sets_last_synced_from_the_server_clock(client, pinned_clock):
    _connect(client, "slack", "T12345")
    r = client.post("/integrations/slack/sync", follow_redirects=False)
    assert r.status_code in (200, 302, 303, 307)
    assert _api_list(client)["slack"]["last_synced_at"] == pinned_clock


def test_sync_shows_the_last_synced_label(client, pinned_clock):
    _connect(client, "slack", "T12345")
    client.post("/integrations/slack/sync", follow_redirects=False)
    html = client.get("/integrations").text
    assert pinned_clock in html
    assert "last synced" in html.lower()


def test_never_synced_provider_shows_a_placeholder(client):
    _connect(client, "slack", "T12345")
    html = client.get("/integrations").text
    assert "never" in html.lower()


def test_sync_unknown_provider_404(client):
    assert client.post("/integrations/slack/sync", follow_redirects=False).status_code == 404


# ---------------------------------------------------------------------------------- HTMX


def test_htmx_connect_returns_the_provider_table_fragment(client):
    r = client.post("/integrations/connect",
                    data={"provider": "slack", "external_id": "T12345"},
                    headers={"HX-Request": "true"}, follow_redirects=False)
    assert r.status_code == 200
    assert 'data-testid="integration-slack"' in r.text
    assert "<html" not in r.text.lower()
    assert_valid_html(r.text, context="HTMX integrations fragment", fragment=True)


def test_htmx_sync_returns_the_fragment_with_the_timestamp(client, pinned_clock):
    _connect(client, "slack", "T12345")
    r = client.post("/integrations/slack/sync",
                    headers={"HX-Request": "true"}, follow_redirects=False)
    assert r.status_code == 200
    assert pinned_clock in r.text
    assert "<html" not in r.text.lower()


def test_non_js_forms_still_work(client):
    """Without HX-Request every mutation must redirect, so the page works without JavaScript."""
    assert _connect(client, "slack", "T12345").status_code in (302, 303, 307)
    assert client.post("/integrations/slack/sync",
                       follow_redirects=False).status_code in (302, 303, 307)
    assert client.post("/integrations/slack/disconnect",
                       follow_redirects=False).status_code in (302, 303, 307)


# ------------------------------------------------------------------------------- markup


def test_integrations_page_is_valid_html(client, pinned_clock):
    """CRB-32 follow-up: new pages are held to the same structural standard."""
    assert_valid_html(client.get("/integrations").text, context="GET /integrations (empty)")
    _connect(client, "slack", "T12345")
    client.post("/integrations/slack/sync", follow_redirects=False)
    assert_valid_html(client.get("/integrations").text, context="GET /integrations (connected)")
