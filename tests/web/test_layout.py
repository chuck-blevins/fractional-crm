"""CRB-29 acceptance test: accessible base layout + nav.

On-rails template assertions for the app shell rendered at ``GET /`` (authenticated).
"""

NAV_LABELS = ["Clients", "Engagements", "Interactions", "Teams", "Integrations", "Import"]


def test_dashboard_renders_accessible_shell(client):
    """Authenticated GET / returns 200 with the skip link, nav, main landmark, and all six section links."""
    r = client.get("/")
    assert r.status_code == 200
    html = r.text
    lower = html.lower()
    # Skip-to-content link that targets the main landmark.
    assert 'href="#main"' in html
    assert "skip" in lower
    # Semantic landmarks: a nav and a <main id="main">.
    assert "<nav" in lower
    assert 'id="main"' in html
    # All six section links present (by visible label).
    for label in NAV_LABELS:
        assert label in html, f"missing nav label: {label}"
    # A logout control somewhere in the chrome.
    assert "/logout" in html


def test_dashboard_still_gated(anon_client):
    """Unauthenticated GET / still redirects to /login (gating preserved from CRB-28)."""
    r = anon_client.get("/", follow_redirects=False)
    assert r.status_code in (302, 303, 307)
    assert "/login" in r.headers["location"]
